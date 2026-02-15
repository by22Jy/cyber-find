"""
Configuration management for CyberFind
"""

import os
from typing import Any, Dict, Optional

import yaml

from .exceptions import ConfigurationError


class Config:
    """Configuration manager for CyberFind"""

    DEFAULT_CONFIG = {
        "general": {
            "timeout": 30,
            "max_threads": 50,
            "retry_attempts": 3,
            "retry_delay": 2,
            "user_agents_rotation": True,
            "rate_limit_delay": 0.5,
        },
        "proxy": {
            "enabled": False,
            "list": [],
            "rotation": True,
        },
        "database": {
            "sqlite_path": "cyberfind.db",
        },
        "output": {
            "default_format": "json",
            "save_all_results": True,
        },
        "advanced": {
            "metadata_extraction": True,
            "cache_results": True,
            "verify_ssl": True,
        },
        "logging": {
            "level": "INFO",
            "file": None,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path or "config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = self.DEFAULT_CONFIG.copy()

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                    self._merge_configs(config, user_config)
            except Exception as e:
                raise ConfigurationError(f"Error loading config file {self.config_path}: {e}")

        return config

    @staticmethod
    def _merge_configs(base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Recursively merge user config into base config"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                Config._merge_configs(base[key], value)
            else:
                base[key] = value

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value by path

        Args:
            path: Path to value (e.g., "general.timeout")
            default: Default value if path not found

        Returns:
            Configuration value
        """
        parts = path.split(".")
        value = self.config

        try:
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, path: str, value: Any) -> None:
        """
        Set configuration value by path

        Args:
            path: Path to value (e.g., "general.timeout")
            value: New value
        """
        parts = path.split(".")
        config = self.config

        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]

        config[parts[-1]] = value

    def save(self, output_path: Optional[str] = None) -> None:
        """
        Save configuration to file

        Args:
            output_path: Path to save config (default: config.yaml)
        """
        output_path = output_path or self.config_path

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Error saving config: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Get full configuration as dictionary"""
        return self.config.copy()
