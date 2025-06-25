"""Configuration management for the task-to-code pipeline."""

import yaml
import os
from typing import Dict, Any, List
from pathlib import Path


class Config:
    """Configuration manager for the task-to-code pipeline."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = config_path
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.template.yaml to {self.config_path} and fill in your values."
            )
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate that all required configuration fields are present."""
        required_fields = [
            'confluence.base_url',
            'confluence.username', 
            'confluence.api_token',
            'project.repository_path',
            'anthropic.api_key'
        ]
        
        for field in required_fields:
            keys = field.split('.')
            current = config
            
            try:
                for key in keys:
                    current = current[key]
                
                if not current or current.startswith('your-'):
                    raise ValueError(f"Please set a valid value for {field}")
                    
            except KeyError:
                raise ValueError(f"Missing required configuration field: {field}")
    
    @property
    def confluence_config(self) -> Dict[str, Any]:
        """Get Confluence API configuration."""
        return self._config['confluence']
    
    @property
    def project_config(self) -> Dict[str, Any]:
        """Get project configuration."""
        return self._config['project']
    
    @property  
    def anthropic_config(self) -> Dict[str, Any]:
        """Get Anthropic API configuration."""
        return self._config['anthropic']
    
    @property
    def output_config(self) -> Dict[str, Any]:
        """Get output configuration."""
        return self._config.get('output', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'confluence.base_url')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        current = self._config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except KeyError:
            return default
