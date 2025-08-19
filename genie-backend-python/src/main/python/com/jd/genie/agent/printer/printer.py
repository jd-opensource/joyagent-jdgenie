"""
Printer interface for handling message output
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from ..enums.agent_type import AgentType


class Printer(ABC):
    """
    Abstract base class for message printing/output
    """
    
    @abstractmethod
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        digital_employee: Optional[str], 
        is_final: bool
    ) -> None:
        """
        Send a message with full parameters
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
            is_final: Whether this is the final message
        """
        pass
    
    @abstractmethod
    def send(self, message_type: str, message: Any) -> None:
        """
        Send a message with minimal parameters
        
        Args:
            message_type: Type of the message
            message: Message content
        """
        pass
    
    @abstractmethod
    def send(self, message_type: str, message: Any, digital_employee: Optional[str]) -> None:
        """
        Send a message with digital employee
        
        Args:
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
        """
        pass
    
    @abstractmethod
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        is_final: bool
    ) -> None:
        """
        Send a message with message ID and final flag
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            is_final: Whether this is the final message
        """
        pass
    
    @abstractmethod
    def close(self) -> None:
        """
        Close the printer and cleanup resources
        """
        pass
    
    @abstractmethod
    def update_agent_type(self, agent_type: AgentType) -> None:
        """
        Update the agent type
        
        Args:
            agent_type: New agent type
        """
        pass