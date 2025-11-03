"""Safety validator for command execution approval."""

from typing import Dict, Any
from .classifier import CommandClassifier
from ..utils.helpers import is_in_scope
from ..utils.logger import get_logger


class SafetyValidator:
    """Validates commands before execution."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize safety validator.
        
        Args:
            config: Safety configuration
        """
        self.config = config
        self.classifier = CommandClassifier(config)
        self.logger = get_logger(__name__)
    
    def validate(self, command: str) -> Dict[str, Any]:
        """
        Validate command for execution.
        
        Args:
            command: Command to validate
            
        Returns:
            Validation result with 'allowed' boolean and 'reason'
        """
        # Classify command
        risk_level = self.classifier.classify(command)
        
        # Check if blacklisted
        if risk_level == 'blacklisted':
            self.logger.warning(
                "command_validation_failed",
                command=command,
                reason="blacklisted",
            )
            return {
                'allowed': False,
                'reason': 'Command is blacklisted as potentially destructive',
                'risk_level': risk_level,
            }
        
        # Validate target scope if applicable
        if not self._validate_scope(command):
            self.logger.warning(
                "command_validation_failed",
                command=command,
                reason="out_of_scope",
            )
            return {
                'allowed': False,
                'reason': 'Target is outside authorized scope',
                'risk_level': risk_level,
            }
        
        # Check rate limits
        if not self._check_rate_limits():
            self.logger.warning(
                "command_validation_failed",
                command=command,
                reason="rate_limit",
            )
            return {
                'allowed': False,
                'reason': 'Rate limit exceeded',
                'risk_level': risk_level,
            }
        
        # Command is allowed
        self.logger.info(
            "command_validation_passed",
            command=command,
            risk_level=risk_level,
        )
        
        return {
            'allowed': True,
            'reason': 'Command passed validation',
            'risk_level': risk_level,
            'requires_approval': risk_level in ['high', 'medium'] and 
                                self.config.get('mode') == 'semi-autonomous',
        }
    
    def _validate_scope(self, command: str) -> bool:
        """
        Validate that command targets are within authorized scope.
        
        Args:
            command: Command to validate
            
        Returns:
            True if within scope or scope validation disabled
        """
        # Check if scope validation is enabled
        target_config = self.config.get('targets', {})
        if not target_config.get('scope_validation', True):
            return True
        
        # Extract potential IP addresses from command
        import re
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, command)
        
        if not ips:
            # No IPs found, allow (might be hostname or non-network command)
            return True
        
        # Check each IP against allowed networks
        allowed_networks = target_config.get('allowed_networks', [])
        excluded_ips = target_config.get('excluded_ips', [])
        
        for ip in ips:
            if not is_in_scope(ip, allowed_networks, excluded_ips):
                self.logger.warning(
                    "target_out_of_scope",
                    ip=ip,
                    command=command,
                )
                return False
        
        return True
    
    def _check_rate_limits(self) -> bool:
        """
        Check if rate limits are exceeded.
        
        Returns:
            True if within limits
        """
        # TODO: Implement actual rate limiting with time-based tracking
        # For now, always return True
        return True
    
    def should_require_approval(self, command: str) -> bool:
        """
        Determine if command requires user approval.
        
        Args:
            command: Command to check
            
        Returns:
            True if approval required
        """
        validation = self.validate(command)
        return validation.get('requires_approval', False)
    
    def get_approval_info(self, command: str, reasoning: str) -> Dict[str, Any]:
        """
        Get information for approval prompt.
        
        Args:
            command: Command requiring approval
            reasoning: AI reasoning for the command
            
        Returns:
            Dictionary with approval information
        """
        risk_details = self.classifier.get_risk_details(command)
        
        return {
            'command': command,
            'risk_level': risk_details['risk_level'],
            'reason': risk_details['reason'],
            'ai_reasoning': reasoning,
        }