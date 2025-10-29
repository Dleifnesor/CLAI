"""Ollama client for LLM communication."""

import asyncio
from typing import Dict, List, Optional, Any
import ollama
from ..utils.logger import get_logger


class LLMCommunicationError(Exception):
    """Exception raised for LLM communication errors."""
    pass


class OllamaClient:
    """Wrapper for Ollama API communication with dolphin3-abliterated model."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama client.
        
        Args:
            config: LLM configuration dictionary
        """
        self.config = config
        self.model = config.get('model', 'huihui_ai/dolphin3-abliterated:8b')
        self.host = config.get('server', {}).get('host', 'localhost')
        self.port = config.get('server', {}).get('port', 11434)
        
        # Initialize Ollama client
        self.client = ollama.Client(host=f"http://{self.host}:{self.port}")
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # Parameters
        self.temperature = config.get('parameters', {}).get('temperature', 0.7)
        self.top_p = config.get('parameters', {}).get('top_p', 0.9)
        self.max_tokens = config.get('parameters', {}).get('max_tokens', 2048)
        self.num_ctx = config.get('parameters', {}).get('num_ctx', 4096)
        
        self.logger = get_logger(__name__)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the response and metadata
            
        Raises:
            LLMCommunicationError: If communication fails
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current prompt
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        try:
            self.logger.info(
                "llm_request",
                model=self.model,
                prompt_length=len(prompt),
                history_length=len(self.conversation_history),
            )
            
            # Make async request
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=messages,
                options={
                    'temperature': self.temperature,
                    'top_p': self.top_p,
                    'num_predict': self.max_tokens,
                    'num_ctx': self.num_ctx,
                },
                stream=stream,
            )
            
            # Extract response content
            response_content = response['message']['content']
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': prompt
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_content
            })
            
            self.logger.info(
                "llm_response",
                response_length=len(response_content),
                total_tokens=response.get('total_duration', 0),
            )
            
            # Parse structured response
            parsed = self._parse_response(response_content)
            
            return {
                'raw_response': response_content,
                'parsed': parsed,
                'metadata': {
                    'model': response.get('model'),
                    'created_at': response.get('created_at'),
                    'total_duration': response.get('total_duration'),
                    'load_duration': response.get('load_duration'),
                    'prompt_eval_count': response.get('prompt_eval_count'),
                    'eval_count': response.get('eval_count'),
                }
            }
            
        except Exception as e:
            self.logger.error(
                "llm_error",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise LLMCommunicationError(f"Failed to generate response: {e}")
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.
        
        Expected format:
        COMMAND: <command>
        TOOL: <tool_name>
        REASONING: <reasoning>
        EXPECTED_OUTCOME: <outcome>
        
        Args:
            content: Response content
            
        Returns:
            Parsed response dictionary
        """
        result = {
            'command': None,
            'tool': None,
            'reasoning': None,
            'expected_outcome': None,
        }
        
        lines = content.strip().split('\n')
        current_key = None
        current_value = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('COMMAND:'):
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                current_key = 'command'
                current_value = [line.replace('COMMAND:', '').strip()]
            elif line.startswith('TOOL:'):
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                current_key = 'tool'
                current_value = [line.replace('TOOL:', '').strip()]
            elif line.startswith('REASONING:'):
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                current_key = 'reasoning'
                current_value = [line.replace('REASONING:', '').strip()]
            elif line.startswith('EXPECTED_OUTCOME:'):
                if current_key and current_value:
                    result[current_key] = '\n'.join(current_value).strip()
                current_key = 'expected_outcome'
                current_value = [line.replace('EXPECTED_OUTCOME:', '').strip()]
            elif current_key and line:
                current_value.append(line)
        
        # Add last key-value pair
        if current_key and current_value:
            result[current_key] = '\n'.join(current_value).strip()
        
        return result
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        self.logger.info("conversation_history_cleared")
    
    def compress_history(self, max_messages: int = 10) -> None:
        """
        Compress conversation history to manage context window.
        
        Args:
            max_messages: Maximum number of messages to keep
        """
        if len(self.conversation_history) > max_messages:
            # Keep the most recent messages
            self.conversation_history = self.conversation_history[-max_messages:]
            self.logger.info(
                "conversation_history_compressed",
                kept_messages=len(self.conversation_history),
            )
    
    def get_history_summary(self) -> str:
        """
        Get a summary of conversation history.
        
        Returns:
            Summary string
        """
        if not self.conversation_history:
            return "No conversation history"
        
        summary_parts = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            role = msg['role']
            content = msg['content'][:100]  # First 100 chars
            summary_parts.append(f"{role}: {content}...")
        
        return "\n".join(summary_parts)
    
    async def test_connection(self) -> bool:
        """
        Test connection to Ollama server.
        
        Returns:
            True if connection successful
        """
        try:
            # Try to list models
            await asyncio.to_thread(self.client.list)
            self.logger.info("ollama_connection_test_passed")
            return True
        except Exception as e:
            self.logger.error(
                "ollama_connection_test_failed",
                error=str(e),
            )
            return False
    
    async def check_model_availability(self) -> bool:
        """
        Check if the configured model is available.
        
        Returns:
            True if model is available
        """
        try:
            models = await asyncio.to_thread(self.client.list)
            model_names = [m['name'] for m in models.get('models', [])]
            
            available = self.model in model_names
            
            self.logger.info(
                "model_availability_check",
                model=self.model,
                available=available,
            )
            
            return available
        except Exception as e:
            self.logger.error(
                "model_availability_check_failed",
                error=str(e),
            )
            return False
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"OllamaClient(model='{self.model}', "
            f"host='{self.host}', port={self.port})"
        )