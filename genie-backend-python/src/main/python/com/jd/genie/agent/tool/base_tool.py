"""
Base tool interface for Genie agents.
工具基接口
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Base interface for all tools in the Genie agent system."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the tool."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get the description of the tool."""
        pass
    
    @abstractmethod
    def to_params(self) -> Dict[str, Any]:
        """Convert tool to parameter format."""
        pass
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute the tool with given input."""
        pass