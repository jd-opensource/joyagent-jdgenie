"""
LLM configuration settings dataclass
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class LLMSettings:
    """
    LLM configuration class
    """
    # Model name
    model: str = "gpt-4o-0806"
    
    # Maximum generated token count
    max_tokens: int = 16384
    
    # Temperature parameter
    temperature: float = 0.0
    
    # API type (openai or azure)
    api_type: Optional[str] = None
    
    # API key
    api_key: str = ""
    
    # API version (for Azure only)
    api_version: Optional[str] = None
    
    # Base URL
    base_url: str = ""
    
    # Interface URL
    interface_url: str = "/v1/chat/completions"
    
    # Function call type
    function_call_type: str = "function_call"
    
    # Maximum input token count
    max_input_tokens: int = 100000
    
    # Additional parameters
    ext_params: Optional[Dict[str, Any]] = field(default_factory=dict)