"""Logging configuration for the Kali AI Command Chaining System."""

import sys
import logging
from pathlib import Path
from typing import Optional
import structlog
from datetime import datetime


def setup_logger(
    name: str = "kali-ai-agent",
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_type: str = "json",
    console_output: bool = True,
) -> structlog.BoundLogger:
    """
    Set up structured logging for the application.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, logs to console only.
        format_type: Log format ('json' or 'text')
        console_output: Whether to output to console
        
    Returns:
        Configured structlog logger
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard logging
    handlers = []
    
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        handlers.append(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        format="%(message)s",
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger(name)


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name. If None, uses default.
        
    Returns:
        Logger instance
    """
    return structlog.get_logger(name or "kali-ai-agent")


class CommandLogger:
    """Specialized logger for command execution tracking."""
    
    def __init__(self, session_id: str, log_dir: str = "logs/sessions"):
        """
        Initialize command logger.
        
        Args:
            session_id: Session identifier
            log_dir: Directory for session logs
        """
        self.session_id = session_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / f"{session_id}.log"
        self.logger = setup_logger(
            name=f"session-{session_id}",
            log_file=str(self.log_file),
            console_output=False,
        )
    
    def log_command(
        self,
        command: str,
        tool: str,
        reasoning: str,
        risk_level: str,
    ) -> None:
        """
        Log a command execution.
        
        Args:
            command: Command being executed
            tool: Tool name
            reasoning: AI reasoning for the command
            risk_level: Risk level (safe, medium, high)
        """
        self.logger.info(
            "command_execution",
            command=command,
            tool=tool,
            reasoning=reasoning,
            risk_level=risk_level,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_output(
        self,
        command: str,
        output: str,
        exit_code: int,
        duration: float,
    ) -> None:
        """
        Log command output.
        
        Args:
            command: Command that was executed
            output: Command output
            exit_code: Exit code
            duration: Execution duration in seconds
        """
        self.logger.info(
            "command_output",
            command=command,
            output=output[:1000],  # Truncate long outputs
            exit_code=exit_code,
            duration=duration,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_discovery(
        self,
        discovery_type: str,
        details: dict,
        severity: str = "info",
    ) -> None:
        """
        Log a security discovery.
        
        Args:
            discovery_type: Type of discovery (host, service, vulnerability, etc.)
            details: Discovery details
            severity: Severity level
        """
        self.logger.info(
            "discovery",
            type=discovery_type,
            details=details,
            severity=severity,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[dict] = None,
    ) -> None:
        """
        Log an error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context
        """
        self.logger.error(
            "error",
            type=error_type,
            message=error_message,
            context=context or {},
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_approval(
        self,
        command: str,
        approved: bool,
        reason: Optional[str] = None,
    ) -> None:
        """
        Log a user approval decision.
        
        Args:
            command: Command requiring approval
            approved: Whether it was approved
            reason: Reason for decision
        """
        self.logger.info(
            "approval_decision",
            command=command,
            approved=approved,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def log_strategy_change(
        self,
        old_strategy: str,
        new_strategy: str,
        reason: str,
    ) -> None:
        """
        Log a strategy adjustment.
        
        Args:
            old_strategy: Previous strategy
            new_strategy: New strategy
            reason: Reason for change
        """
        self.logger.info(
            "strategy_change",
            old_strategy=old_strategy,
            new_strategy=new_strategy,
            reason=reason,
            timestamp=datetime.utcnow().isoformat(),
        )