"""Command classifier for risk assessment."""

import re
from typing import Dict, Any
from .rules import SafetyRules
from ..utils.logger import get_logger


class CommandClassifier:
    """Classifies commands by risk level."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize command classifier.
        
        Args:
            config: Safety configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.rules = SafetyRules()
    
    def classify(self, command: str) -> str:
        """
        Classify command risk level.
        
        Args:
            command: Command to classify
            
        Returns:
            Risk level: 'safe', 'medium', or 'high'
        """
        command_lower = command.lower().strip()
        
        # Check blacklist first
        if self._is_blacklisted(command_lower):
            self.logger.warning(
                "blacklisted_command_detected",
                command=command,
            )
            return 'blacklisted'
        
        # Extract base command
        base_command = command_lower.split()[0] if command_lower else ''
        
        # Check if in safe commands
        if base_command in self.rules.SAFE_COMMANDS:
            # Check for high-risk patterns even in safe commands
            if self._matches_high_risk_pattern(command_lower):
                return 'medium'
            return 'safe'
        
        # Check if in high-risk commands
        if base_command in self.rules.HIGH_RISK_COMMANDS:
            return 'high'
        
        # Check patterns
        if self._matches_high_risk_pattern(command_lower):
            return 'high'
        
        if self._matches_safe_pattern(command_lower):
            return 'safe'
        
        # Default to medium risk for unknown commands
        return 'medium'
    
    def _is_blacklisted(self, command: str) -> bool:
        """Check if command is blacklisted."""
        # Check exact matches
        for blacklisted in self.rules.BLACKLIST:
            if blacklisted.lower() in command:
                return True
        
        # Check patterns
        for pattern in self.rules.BLACKLIST_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        
        # Check config blacklist
        config_blacklist = self.config.get('blacklist', [])
        for item in config_blacklist:
            if item.lower() in command:
                return True
        
        return False
    
    def _matches_high_risk_pattern(self, command: str) -> bool:
        """Check if command matches high-risk patterns."""
        for pattern in self.rules.HIGH_RISK_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def _matches_safe_pattern(self, command: str) -> bool:
        """Check if command matches safe patterns."""
        for pattern in self.rules.SAFE_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False
    
    def get_risk_details(self, command: str) -> Dict[str, Any]:
        """
        Get detailed risk assessment for command.
        
        Args:
            command: Command to assess
            
        Returns:
            Dictionary with risk details
        """
        risk_level = self.classify(command)
        
        details = {
            'risk_level': risk_level,
            'requires_approval': risk_level in ['high', 'medium'] and 
                                self.config.get('mode') == 'semi-autonomous',
            'reason': self._get_risk_reason(command, risk_level),
        }
        
        return details
    
    def _get_risk_reason(self, command: str, risk_level: str) -> str:
        """Get reason for risk classification."""
        if risk_level == 'blacklisted':
            return "Command is blacklisted as potentially destructive"
        elif risk_level == 'high':
            return "Command performs exploitation or modification operations"
        elif risk_level == 'medium':
            return "Command requires elevated privileges or has potential impact"
        else:
            return "Command performs safe reconnaissance operations"