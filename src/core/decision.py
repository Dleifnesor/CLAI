"""Decision engine for intelligent command selection."""

from typing import Dict, List, Any
from ..utils.logger import get_logger


class DecisionEngine:
    """Makes intelligent decisions about next commands."""
    
    def __init__(self, llm_client):
        """
        Initialize decision engine.
        
        Args:
            llm_client: LLM client instance
        """
        self.llm = llm_client
        self.logger = get_logger(__name__)
    
    async def select_next_command(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select optimal next command based on context.
        
        Args:
            context: Current context including history and discoveries
            
        Returns:
            Command information dictionary
        """
        from ..llm.prompts import PromptTemplates
        
        # Build prompt for command generation
        prompt = PromptTemplates.command_prompt(context)
        system_prompt = PromptTemplates.system_prompt()
        
        # Generate command from LLM
        response = await self.llm.generate(prompt, system_prompt)
        
        parsed = response.get('parsed', {})
        
        command_info = {
            'command': parsed.get('command'),
            'tool': parsed.get('tool'),
            'reasoning': parsed.get('reasoning'),
            'expected_outcome': parsed.get('expected_outcome'),
            'raw_response': response.get('raw_response'),
        }
        
        self.logger.info(
            "command_selected",
            command=command_info['command'],
            tool=command_info['tool'],
        )
        
        return command_info
    
    async def assess_objective_completion(
        self,
        objective: str,
        discoveries: Dict[str, Any],
        command_count: int,
    ) -> Dict[str, Any]:
        """
        Assess if objective has been completed.
        
        Args:
            objective: Original objective
            discoveries: All discoveries made
            command_count: Number of commands executed
            
        Returns:
            Assessment dictionary
        """
        from ..llm.prompts import PromptTemplates
        
        prompt = PromptTemplates.objective_assessment_prompt(
            objective,
            discoveries,
            command_count,
        )
        
        response = await self.llm.generate(prompt)
        
        # Parse completion status from response
        raw_response = response.get('raw_response', '').upper()
        
        if 'COMPLETE' in raw_response and 'INCOMPLETE' not in raw_response:
            status = 'complete'
        elif 'PARTIAL' in raw_response:
            status = 'partial'
        else:
            status = 'incomplete'
        
        return {
            'status': status,
            'reasoning': response.get('raw_response'),
            'recommendations': self._extract_recommendations(response.get('raw_response', '')),
        }
    
    async def request_strategy_adjustment(
        self,
        analysis: Dict[str, Any],
        failed_attempts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Request strategy adjustment from LLM.
        
        Args:
            analysis: Current situation analysis
            failed_attempts: Recent failed attempts
            
        Returns:
            New strategy information
        """
        from ..llm.prompts import PromptTemplates
        
        prompt = PromptTemplates.strategy_adjustment_prompt(
            analysis,
            failed_attempts,
        )
        
        response = await self.llm.generate(prompt)
        
        return {
            'new_strategy': response.get('raw_response'),
            'reasoning': response.get('parsed', {}).get('reasoning', ''),
        }
    
    async def analyze_error(
        self,
        command: str,
        error: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze error and suggest recovery.
        
        Args:
            command: Failed command
            error: Error message
            context: Current context
            
        Returns:
            Error analysis and recovery suggestion
        """
        from ..llm.prompts import PromptTemplates
        
        prompt = PromptTemplates.error_analysis_prompt(
            command,
            error,
            context,
        )
        
        response = await self.llm.generate(prompt)
        
        return {
            'analysis': response.get('raw_response'),
            'recovery_action': self._extract_recovery_action(response.get('raw_response', '')),
        }
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from LLM response."""
        recommendations = []
        
        # Look for numbered or bulleted lists
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                clean_line = line.lstrip('0123456789.-• ')
                if clean_line:
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _extract_recovery_action(self, text: str) -> str:
        """Extract recovery action from error analysis."""
        # Look for action-oriented sentences
        lines = text.split('\n')
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in ['retry', 'try', 'use', 'run', 'execute']):
                return line.strip()
        
        return "Try alternative approach"