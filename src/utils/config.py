"""Configuration management for the Kali AI Command Chaining System."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


class ConfigLoader:
    """Loads and manages system configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._load_env_overrides()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try to find config.yaml in the project root
        current_dir = Path(__file__).parent.parent.parent
        config_file = current_dir / "config.yaml"
        
        if config_file.exists():
            return str(config_file)
        
        # Fallback to /etc if running system-wide
        system_config = Path("/etc/kali-ai-agent/config.yaml")
        if system_config.exists():
            return str(system_config)
        
        raise FileNotFoundError(
            "Configuration file not found. Please create config.yaml"
        )
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {e}")
    
    def _load_env_overrides(self) -> None:
        """Load environment variable overrides."""
        load_dotenv()
        
        # Override LLM settings from environment
        if os.getenv("OLLAMA_HOST"):
            self.config["llm"]["server"]["host"] = os.getenv("OLLAMA_HOST")
        
        if os.getenv("OLLAMA_PORT"):
            self.config["llm"]["server"]["port"] = int(os.getenv("OLLAMA_PORT"))
        
        if os.getenv("OLLAMA_MODEL"):
            self.config["llm"]["model"] = os.getenv("OLLAMA_MODEL")
        
        # Override logging level
        if os.getenv("LOG_LEVEL"):
            self.config["logging"]["level"] = os.getenv("LOG_LEVEL")
        
        # Override safety mode
        if os.getenv("SAFETY_MODE"):
            self.config["safety"]["mode"] = os.getenv("SAFETY_MODE")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'llm.server.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key: Configuration key in dot notation
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Path to save to. If None, uses original path.
        """
        save_path = path or self.config_path
        
        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def validate(self) -> bool:
        """
        Validate configuration completeness and correctness.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = [
            "llm.provider",
            "llm.model",
            "llm.server.host",
            "llm.server.port",
            "safety.mode",
            "execution.timeout.default",
            "logging.level",
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                raise ValueError(f"Missing required configuration: {key}")
        
        # Validate safety mode
        valid_modes = ["semi-autonomous", "interactive", "autonomous"]
        if self.get("safety.mode") not in valid_modes:
            raise ValueError(
                f"Invalid safety mode. Must be one of: {', '.join(valid_modes)}"
            )
        
        # Validate logging level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.get("logging.level") not in valid_levels:
            raise ValueError(
                f"Invalid logging level. Must be one of: {', '.join(valid_levels)}"
            )
        
        return True
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.get("llm", {})
    
    def get_safety_config(self) -> Dict[str, Any]:
        """Get safety configuration."""
        return self.get("safety", {})
    
    def get_execution_config(self) -> Dict[str, Any]:
        """Get execution configuration."""
        return self.get("execution", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get("logging", {})
    
    def get_tool_paths(self) -> Dict[str, str]:
        """Get tool paths configuration."""
        return self.get("tools.paths", {})
    
    def get_target_config(self) -> Dict[str, Any]:
        """Get target configuration."""
        return self.get("targets", {})
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get AI agent configuration."""
        return self.get("agent", {})
    
    def is_tool_available(self, tool_name: str) -> bool:
        """
        Check if a tool is configured and available.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            True if tool is available
        """
        tool_path = self.get(f"tools.paths.{tool_name}")
        if not tool_path:
            return False
        
        return Path(tool_path).exists()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"ConfigLoader(config_path='{self.config_path}')"