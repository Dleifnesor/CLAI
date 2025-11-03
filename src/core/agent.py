"""Main AI agent for autonomous command chaining."""

import asyncio
from typing import Dict, Any, Optional
from enum import Enum

from ..llm.client import OllamaClient
from ..llm.prompts import PromptTemplates
from ..execution.executor import CommandExecutor
from ..execution.parser import OutputParser
from ..execution.interpreter import ResultInterpreter
from ..safety.validator import SafetyValidator
from .state import StateManager
from .decision import DecisionEngine
from ..utils.logger import get_logger


class AgentState(Enum):
    """Agent execution states."""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    EXECUTING = "executing"
    ANALYZING = "analyzing"
    AWAITING_APPROVAL = "awaiting_approval"
    ADJUSTING_STRATEGY = "adjusting_strategy"
    COMPLETED = "completed"
    FAILED = "failed"


class AIAgent:
    """Central AI agent orchestrator."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        llm_client: OllamaClient,
        executor: CommandExecutor,
        state_manager: StateManager,
        approval_callback: Optional[callable] = None,
        progress_callback: Optional[callable] = None,
    ):
        """
        Initialize AI agent.
        
        Args:
            config: Agent configuration
            llm_client: LLM client instance
            executor: Command executor instance
            state_manager: State manager instance
            approval_callback: Callback for approval requests (command, info) -> bool
            progress_callback: Callback for progress updates (state, info) -> None
        """
        self.config = config
        self.llm = llm_client
        self.executor = executor
        self.state = state_manager
        self.approval_callback = approval_callback
        self.progress_callback = progress_callback
        
        self.parser = OutputParser()
        self.interpreter = ResultInterpreter()
        self.decision = DecisionEngine(llm_client)
        
        self.current_state = AgentState.INITIALIZING
        self.max_commands = config.get('max_commands', 50)
        self.max_retries = config.get('max_retries', 3)
        self.strategy_adjustment_threshold = config.get('strategy_adjustment_threshold', 3)
        
        self.logger = get_logger(__name__)
    
    async def execute_objective(self, objective: str) -> Dict[str, Any]:
        """
        Execute security objective autonomously.
        
        Args:
            objective: Security objective to accomplish
            
        Returns:
            Final report dictionary
        """
        self.logger.info("agent_started", objective=objective)
        self.state.set_objective(objective)
        
        try:
            # Planning phase
            self.current_state = AgentState.PLANNING
            await self._notify_progress("Planning approach...")
            
            # Main execution loop
            consecutive_failures = 0
            
            while not await self._is_objective_complete():
                # Check limits
                if len(self.state.command_history) >= self.max_commands:
                    self.logger.warning("max_commands_reached")
                    break
                
                # Get next command
                self.current_state = AgentState.EXECUTING
                await self._notify_progress("Generating next command...")
                
                command_info = await self.decision.select_next_command(
                    self.state.get_context_for_llm()
                )
                
                if not command_info.get('command'):
                    self.logger.error("no_command_generated")
                    break
                
                # Check if approval needed
                if self.executor.safety.should_require_approval(command_info['command']):
                    self.current_state = AgentState.AWAITING_APPROVAL
                    
                    if not await self._request_approval(command_info):
                        self.logger.info("command_rejected_by_user")
                        # Ask LLM for alternative
                        continue
                
                # Execute command
                await self._notify_progress(f"Executing: {command_info['command']}")
                
                result = await self.executor.execute(command_info['command'])
                
                # Parse and interpret results
                self.current_state = AgentState.ANALYZING
                await self._notify_progress("Analyzing results...")
                
                parsed = self.parser.parse(result, command_info.get('tool'))
                interpretation = self.interpreter.interpret(parsed)
                
                # Update state
                self.state.add_command_result(
                    command=command_info['command'],
                    tool=command_info.get('tool', 'unknown'),
                    reasoning=command_info.get('reasoning', ''),
                    result=result,
                    analysis={
                        'parsed': parsed,
                        'interpretation': interpretation,
                        'risk_level': self.executor.safety.classifier.classify(command_info['command']),
                    },
                )
                
                # Handle failures
                if not result.get('success'):
                    consecutive_failures += 1
                    
                    if consecutive_failures >= self.strategy_adjustment_threshold:
                        # Request strategy adjustment
                        self.current_state = AgentState.ADJUSTING_STRATEGY
                        await self._adjust_strategy()
                        consecutive_failures = 0
                    else:
                        # Analyze error and try recovery
                        await self._handle_error(command_info, result)
                else:
                    consecutive_failures = 0
                
                # Small delay between commands
                await asyncio.sleep(1)
            
            # Completion
            self.current_state = AgentState.COMPLETED
            await self._notify_progress("Objective complete!")
            
            report = self.state.generate_report()
            
            self.logger.info(
                "agent_completed",
                session_id=self.state.session_id,
                commands=len(self.state.command_history),
                progress=self.state.calculate_progress(),
            )
            
            return report
            
        except Exception as e:
            self.current_state = AgentState.FAILED
            self.logger.error(
                "agent_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
    
    async def _is_objective_complete(self) -> bool:
        """Check if objective has been achieved."""
        # Don't check completion too early
        if len(self.state.command_history) < 3:
            return False
        
        # Check every 5 commands
        if len(self.state.command_history) % 5 != 0:
            return False
        
        # Ask LLM to assess completion
        assessment = await self.decision.assess_objective_completion(
            self.state.objective,
            self.state.discoveries,
            len(self.state.command_history),
        )
        
        return assessment.get('status') == 'complete'
    
    async def _request_approval(self, command_info: Dict[str, Any]) -> bool:
        """
        Request user approval for command.
        
        Args:
            command_info: Command information
            
        Returns:
            True if approved
        """
        if self.approval_callback:
            approval_info = self.executor.safety.get_approval_info(
                command_info['command'],
                command_info.get('reasoning', ''),
            )
            return await asyncio.to_thread(self.approval_callback, command_info['command'], approval_info)
        
        # Default to approved if no callback
        return True
    
    async def _notify_progress(self, message: str) -> None:
        """Notify progress callback."""
        if self.progress_callback:
            await asyncio.to_thread(
                self.progress_callback,
                self.current_state.value,
                {
                    'message': message,
                    'progress': self.state.calculate_progress(),
                    'commands': len(self.state.command_history),
                }
            )
    
    async def _adjust_strategy(self) -> None:
        """Adjust strategy after repeated failures."""
        self.logger.info("adjusting_strategy")
        
        await self._notify_progress("Adjusting strategy...")
        
        new_strategy = await self.decision.request_strategy_adjustment(
            {'summary': 'Multiple failures encountered'},
            self.state.get_recent_failures(),
        )
        
        self.state.add_strategy_change(
            old_strategy='current',
            new_strategy=new_strategy.get('new_strategy', ''),
            reason='Multiple command failures',
        )
    
    async def _handle_error(self, command_info: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Handle command execution error.
        
        Args:
            command_info: Command information
            result: Execution result with error
        """
        self.logger.warning(
            "handling_error",
            command=command_info['command'],
            error=result.get('error'),
        )
        
        # Analyze error with LLM
        error_analysis = await self.decision.analyze_error(
            command_info['command'],
            result.get('error', ''),
            self.state.get_context_for_llm(),
        )
        
        self.logger.info(
            "error_analyzed",
            recovery_action=error_analysis.get('recovery_action'),
        )