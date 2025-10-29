"""Context management for LLM conversations."""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class ContextManager:
    """Manages conversation context and history for the LLM."""
    
    def __init__(self, max_context_size: int = 10):
        """
        Initialize context manager.
        
        Args:
            max_context_size: Maximum number of recent commands to keep in full detail
        """
        self.max_context_size = max_context_size
        self.objective: str = ""
        self.command_history: List[Dict[str, Any]] = []
        self.discoveries: Dict[str, List[Any]] = {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
        }
        self.context_window: List[Dict[str, Any]] = []
    
    def set_objective(self, objective: str) -> None:
        """
        Set the security objective.
        
        Args:
            objective: Security objective string
        """
        self.objective = objective
    
    def add_command_result(
        self,
        command: str,
        tool: str,
        reasoning: str,
        output: str,
        exit_code: int,
        analysis: Dict[str, Any],
    ) -> None:
        """
        Add a command execution result to context.
        
        Args:
            command: Command that was executed
            tool: Tool name
            reasoning: AI reasoning for the command
            output: Command output
            exit_code: Exit code
            analysis: Analysis of the results
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'command': command,
            'tool': tool,
            'reasoning': reasoning,
            'output': output[:1000],  # Truncate long outputs
            'exit_code': exit_code,
            'analysis': analysis,
        }
        
        self.command_history.append(entry)
        self._update_context_window(entry)
        self._update_discoveries(analysis)
    
    def _update_context_window(self, entry: Dict[str, Any]) -> None:
        """
        Update the sliding context window.
        
        Args:
            entry: Command entry to add
        """
        self.context_window.append(entry)
        
        # Keep only recent entries in full detail
        if len(self.context_window) > self.max_context_size:
            # Compress older entries
            self.context_window = self._compress_old_entries(self.context_window)
    
    def _compress_old_entries(
        self,
        entries: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Compress old context entries to save space.
        
        Args:
            entries: List of context entries
            
        Returns:
            Compressed list with recent entries in full detail
        """
        if len(entries) <= self.max_context_size:
            return entries
        
        # Keep recent entries in full detail
        recent = entries[-self.max_context_size:]
        
        # Compress older entries (keep only essential info)
        old = entries[:-self.max_context_size]
        compressed_old = []
        
        for entry in old:
            compressed_old.append({
                'timestamp': entry['timestamp'],
                'command': entry['command'],
                'tool': entry['tool'],
                'exit_code': entry['exit_code'],
                'summary': entry.get('analysis', {}).get('interpretation', {}).get('summary', 'No summary'),
            })
        
        return compressed_old + recent
    
    def _update_discoveries(self, analysis: Dict[str, Any]) -> None:
        """
        Update discoveries from analysis.
        
        Args:
            analysis: Analysis containing discoveries
        """
        interpretation = analysis.get('interpretation', {})
        
        # Add hosts
        if 'hosts' in interpretation:
            for host in interpretation['hosts']:
                if host not in self.discoveries['hosts']:
                    self.discoveries['hosts'].append(host)
        
        # Add services
        if 'services' in interpretation:
            for service in interpretation['services']:
                if service not in self.discoveries['services']:
                    self.discoveries['services'].append(service)
        
        # Add vulnerabilities
        if 'vulnerabilities' in interpretation:
            for vuln in interpretation['vulnerabilities']:
                if vuln not in self.discoveries['vulnerabilities']:
                    self.discoveries['vulnerabilities'].append(vuln)
        
        # Add credentials
        if 'credentials' in interpretation:
            for cred in interpretation['credentials']:
                if cred not in self.discoveries['credentials']:
                    self.discoveries['credentials'].append(cred)
    
    def get_full_context(self) -> Dict[str, Any]:
        """
        Get complete context for LLM.
        
        Returns:
            Dictionary containing full context
        """
        return {
            'objective': self.objective,
            'command_count': len(self.command_history),
            'recent_commands': self.context_window,
            'discoveries': self.discoveries,
            'current_progress': self._calculate_progress(),
        }
    
    def _calculate_progress(self) -> float:
        """
        Calculate progress toward objective.
        
        Returns:
            Progress percentage (0-100)
        """
        # Simple heuristic based on discoveries and commands
        # This can be made more sophisticated based on objective type
        
        total_discoveries = (
            len(self.discoveries['hosts']) +
            len(self.discoveries['services']) +
            len(self.discoveries['vulnerabilities']) +
            len(self.discoveries['credentials'])
        )
        
        # Weight different factors
        discovery_score = min(50, total_discoveries * 5)  # Max 50% from discoveries
        command_score = min(30, len(self.command_history) * 3)  # Max 30% from commands
        
        # Check for vulnerabilities found (indicates deeper progress)
        vuln_score = min(20, len(self.discoveries['vulnerabilities']) * 10)  # Max 20%
        
        return min(100.0, discovery_score + command_score + vuln_score)
    
    def get_summary(self) -> str:
        """
        Get a text summary of current context.
        
        Returns:
            Summary string
        """
        summary_parts = [
            f"Objective: {self.objective}",
            f"Commands Executed: {len(self.command_history)}",
            f"Progress: {self._calculate_progress():.1f}%",
            "",
            "Discoveries:",
            f"  - Hosts: {len(self.discoveries['hosts'])}",
            f"  - Services: {len(self.discoveries['services'])}",
            f"  - Vulnerabilities: {len(self.discoveries['vulnerabilities'])}",
            f"  - Credentials: {len(self.discoveries['credentials'])}",
        ]
        
        if self.context_window:
            summary_parts.append("")
            summary_parts.append("Recent Commands:")
            for entry in self.context_window[-3:]:
                summary_parts.append(f"  - {entry['command']} ({entry['tool']})")
        
        return "\n".join(summary_parts)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export context to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            'objective': self.objective,
            'command_history': self.command_history,
            'discoveries': self.discoveries,
            'context_window': self.context_window,
            'progress': self._calculate_progress(),
        }
    
    def export_to_json(self) -> str:
        """
        Export context to JSON string.
        
        Returns:
            JSON string
        """
        return json.dumps(self.export_to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextManager':
        """
        Create ContextManager from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            ContextManager instance
        """
        manager = cls()
        manager.objective = data.get('objective', '')
        manager.command_history = data.get('command_history', [])
        manager.discoveries = data.get('discoveries', {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
        })
        manager.context_window = data.get('context_window', [])
        return manager
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ContextManager':
        """
        Create ContextManager from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            ContextManager instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def clear(self) -> None:
        """Clear all context."""
        self.objective = ""
        self.command_history = []
        self.discoveries = {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
        }
        self.context_window = []
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ContextManager(objective='{self.objective[:50]}...', "
            f"commands={len(self.command_history)}, "
            f"progress={self._calculate_progress():.1f}%)"
        )