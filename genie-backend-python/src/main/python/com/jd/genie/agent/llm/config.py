"""
Configuration utilities for LLM settings
"""
import logging
import yaml
from pathlib import Path
from typing import Dict, Optional

from .llm_settings import LLMSettings

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration utility class for loading LLM settings
    """
    
    _config_cache: Optional[Dict] = None
    _llm_settings_map: Optional[Dict[str, LLMSettings]] = None
    
    @classmethod
    def get_llm_config(cls, model_name: str) -> LLMSettings:
        """
        Get LLM configuration for a specific model
        
        Args:
            model_name: Name of the model to get configuration for
            
        Returns:
            LLMSettings object with configuration for the model
        """
        # Try to get from application context or config map first
        if cls._llm_settings_map is not None:
            return cls._llm_settings_map.get(model_name, cls._get_default_config())
        
        return cls._get_default_config()
    
    @classmethod
    def _get_default_config(cls) -> LLMSettings:
        """
        Load default LLM configuration from application.yml
        
        Returns:
            Default LLMSettings object
        """
        try:
            # Load configuration from application.yml
            config_path = Path(__file__).parent.parent.parent.parent.parent.parent / "resources" / "application.yml"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    
                # Extract LLM default configuration
                llm_default = config.get('llm', {}).get('default', {})
                
                return LLMSettings(
                    model=llm_default.get('model', 'gpt-4o-0806'),
                    max_tokens=int(llm_default.get('max_tokens', 16384)),
                    temperature=float(llm_default.get('temperature', 0.0)),
                    base_url=llm_default.get('base_url', ''),
                    interface_url=llm_default.get('interface_url', '/v1/chat/completions'),
                    function_call_type=llm_default.get('function_call_type', 'function_call'),
                    api_key=llm_default.get('apikey', ''),
                    max_input_tokens=int(llm_default.get('max_input_tokens', 100000))
                )
            else:
                logger.warning(f"Configuration file not found at {config_path}, using default settings")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}, using default settings")
        
        # Return default configuration if file loading fails
        return LLMSettings(
            model='gpt-4o-0806',
            max_tokens=16384,
            temperature=0.0,
            base_url='',
            interface_url='/v1/chat/completions',
            function_call_type='function_call',
            api_key='',
            max_input_tokens=100000
        )
    
    @classmethod
    def set_llm_settings_map(cls, settings_map: Dict[str, LLMSettings]) -> None:
        """
        Set the LLM settings map (typically called by application context)
        
        Args:
            settings_map: Dictionary mapping model names to LLMSettings
        """
        cls._llm_settings_map = settings_map
    
    @classmethod
    def load_yaml_config(cls, config_path: str) -> Dict:
        """
        Load configuration from a YAML file
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            Dictionary containing the configuration
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading YAML configuration from {config_path}: {e}")
            return {}