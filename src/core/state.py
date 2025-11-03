"""State management for AI agent sessions."""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..utils.helpers import generate_session_id
from ..utils.logger import get_logger, CommandLogger


class StateManager:
    """Manages agent state and session persistence."""
    
    def __init__(self, session_id: Optional[str] = None, session_dir: str = "logs/sessions"):
        """
        Initialize state manager.
        
        Args:
            session_id: Session identifier (generates new if None)
            session_dir: Directory for session storage
        """
        self.session_id = session_id or generate_session_id()
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self.objective: str = ""
        self.command_history: List[Dict[str, Any]] = []
        self.discoveries: Dict[str, List[Any]] = {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
        }
        self.failed_attempts: List[Dict[str, Any]] = []
        self.strategy_changes: List[Dict[str, Any]] = []
        
        self.logger = get_logger(__name__)
        self.command_logger = CommandLogger(self.session_id, str(self.session_dir))
    
    def set_objective(self, objective: str) -> None:
        """Set the security objective."""
        self.objective = objective
        self.logger.info("objective_set", objective=objective, session_id=self.session_id)
    
    def add_command_result(
        self,
        command: str,
        tool: str,
        reasoning: str,
        result: Dict[str, Any],
        analysis: Dict[str, Any],
    ) -> None:
        """
        Add command execution result to state.
        
        Args:
            command: Command executed
            tool: Tool name
            reasoning: AI reasoning
            result: Execution result
            analysis: Result analysis
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'command': command,
            'tool': tool,
            'reasoning': reasoning,
            'output': result.get('output', '')[:1000],  # Truncate
            'error': result.get('error', ''),
            'exit_code': result.get('exit_code', 0),
            'duration': result.get('duration', 0),
            'analysis': analysis,
        }
        
        self.command_history.append(entry)
        
        # Log command execution
        self.command_logger.log_command(
            command=command,
            tool=tool,
            reasoning=reasoning,
            risk_level=analysis.get('risk_level', 'unknown'),
        )
        
        self.command_logger.log_output(
            command=command,
            output=result.get('output', ''),
            exit_code=result.get('exit_code', 0),
            duration=result.get('duration', 0),
        )
        
        # Update discoveries
        self._update_discoveries(analysis)
        
        # Track failures
        if not result.get('success'):
            self.failed_attempts.append({
                'command': command,
                'error': result.get('error', ''),
                'timestamp': datetime.utcnow().isoformat(),
            })
        
        # Auto-save
        self.save()
    
    def _update_discoveries(self, analysis: Dict[str, Any]) -> None:
        """Update discoveries from analysis."""
        interpretation = analysis.get('interpretation', {})
        
        # Add hosts
        for host in interpretation.get('hosts', []):
            if host not in self.discoveries['hosts']:
                self.discoveries['hosts'].append(host)
                self.command_logger.log_discovery(
                    discovery_type='host',
                    details=host,
                    severity='info',
                )
        
        # Add services
        for service in interpretation.get('services', []):
            if service not in self.discoveries['services']:
                self.discoveries['services'].append(service)
                self.command_logger.log_discovery(
                    discovery_type='service',
                    details=service,
                    severity='info',
                )
        
        # Add vulnerabilities
        for vuln in interpretation.get('vulnerabilities', []):
            if vuln not in self.discoveries['vulnerabilities']:
                self.discoveries['vulnerabilities'].append(vuln)
                self.command_logger.log_discovery(
                    discovery_type='vulnerability',
                    details=vuln,
                    severity=vuln.get('severity', 'medium'),
                )
        
        # Add credentials
        for cred in interpretation.get('credentials', []):
            if cred not in self.discoveries['credentials']:
                self.discoveries['credentials'].append(cred)
                self.command_logger.log_discovery(
                    discovery_type='credential',
                    details=cred,
                    severity='high',
                )
    
    def add_strategy_change(self, old_strategy: str, new_strategy: str, reason: str) -> None:
        """Record a strategy change."""
        change = {
            'timestamp': datetime.utcnow().isoformat(),
            'old_strategy': old_strategy,
            'new_strategy': new_strategy,
            'reason': reason,
        }
        self.strategy_changes.append(change)
        
        self.command_logger.log_strategy_change(
            old_strategy=old_strategy,
            new_strategy=new_strategy,
            reason=reason,
        )
    
    def get_recent_failures(self, count: int = 3) -> List[Dict[str, Any]]:
        """Get recent failed attempts."""
        return self.failed_attempts[-count:] if self.failed_attempts else []
    
    def calculate_progress(self) -> float:
        """
        Calculate progress toward objective.
        
        Returns:
            Progress percentage (0-100)
        """
        # Heuristic based on discoveries and commands
        total_discoveries = (
            len(self.discoveries['hosts']) +
            len(self.discoveries['services']) +
            len(self.discoveries['vulnerabilities']) +
            len(self.discoveries['credentials'])
        )
        
        # Weight different factors
        discovery_score = min(50, total_discoveries * 5)
        command_score = min(30, len(self.command_history) * 3)
        vuln_score = min(20, len(self.discoveries['vulnerabilities']) * 10)
        
        return min(100.0, discovery_score + command_score + vuln_score)
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Get context for LLM."""
        return {
            'objective': self.objective,
            'session_id': self.session_id,
            'command_count': len(self.command_history),
            'recent_commands': self.command_history[-5:],  # Last 5
            'discoveries': self.discoveries,
            'current_progress': self.calculate_progress(),
            'failed_attempts': self.get_recent_failures(),
        }
    
    def save(self) -> None:
        """Save session to disk."""
        session_file = self.session_dir / f"{self.session_id}.json"
        
        data = {
            'session_id': self.session_id,
            'objective': self.objective,
            'command_history': self.command_history,
            'discoveries': self.discoveries,
            'failed_attempts': self.failed_attempts,
            'strategy_changes': self.strategy_changes,
            'progress': self.calculate_progress(),
            'created_at': self.command_history[0]['timestamp'] if self.command_history else datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
        }
        
        with open(session_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info("session_saved", session_id=self.session_id)
    
    @classmethod
    def load(cls, session_id: str, session_dir: str = "logs/sessions") -> 'StateManager':
        """
        Load session from disk.
        
        Args:
            session_id: Session identifier
            session_dir: Directory containing sessions
            
        Returns:
            StateManager instance
        """
        session_file = Path(session_dir) / f"{session_id}.json"
        
        if not session_file.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        manager = cls(session_id, session_dir)
        manager.objective = data.get('objective', '')
        manager.command_history = data.get('command_history', [])
        manager.discoveries = data.get('discoveries', {
            'hosts': [],
            'services': [],
            'vulnerabilities': [],
            'credentials': [],
        })
        manager.failed_attempts = data.get('failed_attempts', [])
        manager.strategy_changes = data.get('strategy_changes', [])
        
        manager.logger.info("session_loaded", session_id=session_id)
        
        return manager
    
    @classmethod
    def list_sessions(cls, session_dir: str = "logs/sessions") -> List[Dict[str, Any]]:
        """
        List all saved sessions.
        
        Args:
            session_dir: Directory containing sessions
            
        Returns:
            List of session summaries
        """
        session_path = Path(session_dir)
        if not session_path.exists():
            return []
        
        sessions = []
        for session_file in session_path.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                
                sessions.append({
                    'session_id': data.get('session_id'),
                    'objective': data.get('objective', '')[:100],
                    'progress': data.get('progress', 0),
                    'commands': len(data.get('command_history', [])),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                })
            except Exception:
                continue
        
        # Sort by updated_at descending
        sessions.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return sessions
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final report."""
        return {
            'session_id': self.session_id,
            'objective': self.objective,
            'progress': self.calculate_progress(),
            'commands_executed': len(self.command_history),
            'discoveries': {
                'hosts': len(self.discoveries['hosts']),
                'services': len(self.discoveries['services']),
                'vulnerabilities': len(self.discoveries['vulnerabilities']),
                'credentials': len(self.discoveries['credentials']),
            },
            'detailed_discoveries': self.discoveries,
            'failed_attempts': len(self.failed_attempts),
            'strategy_changes': len(self.strategy_changes),
            'duration': self._calculate_duration(),
        }
    
    def _calculate_duration(self) -> float:
        """Calculate total session duration."""
        if not self.command_history:
            return 0.0
        
        return sum(cmd.get('duration', 0) for cmd in self.command_history)