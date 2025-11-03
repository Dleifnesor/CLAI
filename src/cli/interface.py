"""CLI interface controller."""

from typing import Dict, Any
from .display import DisplayManager
from ..core.state import StateManager


class CLIInterface:
    """Main CLI interface controller."""
    
    def __init__(self):
        """Initialize CLI interface."""
        self.display = DisplayManager()
    
    def approval_callback(self, command: str, info: Dict[str, Any]) -> bool:
        """
        Handle approval requests.
        
        Args:
            command: Command requiring approval
            info: Approval information
            
        Returns:
            True if approved
        """
        return self.display.show_approval_request(command, info)
    
    def progress_callback(self, state: str, info: Dict[str, Any]) -> None:
        """
        Handle progress updates.
        
        Args:
            state: Current agent state
            info: Progress information
        """
        message = info.get('message', '')
        progress = info.get('progress', 0)
        
        self.display.show_progress(progress, message)
    
    def show_command_execution(
        self,
        command: str,
        tool: str,
        reasoning: str,
        risk_level: str,
    ):
        """Show command being executed."""
        self.display.show_command(command, tool, reasoning, risk_level)
    
    def show_command_result(self, result: Dict[str, Any], tool: str):
        """Show command execution result."""
        output = result.get('output', '')
        success = result.get('success', False)
        
        if output:
            self.display.show_output(output, tool, success)
        
        if not success:
            error = result.get('error', 'Unknown error')
            self.display.show_error(error, "Command Failed")
    
    def show_discoveries(self, discoveries: Dict[str, Any]):
        """Show current discoveries."""
        self.display.show_discoveries(discoveries)
    
    def show_final_report(self, report: Dict[str, Any]):
        """Show final assessment report."""
        self.display.show_report(report)
    
    def list_sessions(self):
        """List all saved sessions."""
        sessions = StateManager.list_sessions()
        
        if not sessions:
            self.display.show_info("No saved sessions found")
            return
        
        self.display.console.print("\n[bold cyan]📋 Saved Sessions:[/bold cyan]\n")
        
        for session in sessions:
            progress = session.get('progress', 0)
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))
            
            self.display.console.print(
                f"  [cyan]•[/cyan] {session['session_id']}\n"
                f"    Objective: {session['objective']}\n"
                f"    Progress: [{progress_bar}] {progress:.1f}%\n"
                f"    Commands: {session['commands']}\n"
                f"    Updated: {session.get('updated_at', 'unknown')}\n"
            )
        
        self.display.console.print(
            f"\n[dim]Total: {len(sessions)} sessions[/dim]"
        )
        self.display.console.print(
            "[dim]Resume with: clai --resume <session-id>[/dim]\n"
        )