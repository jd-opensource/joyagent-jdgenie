"""
Log printer implementation for outputting messages to logs
"""
import json
import logging
from typing import Any, Optional

from .printer import Printer
from ..enums.agent_type import AgentType

logger = logging.getLogger(__name__)


class LogPrinter(Printer):
    """
    Log printer implementation that outputs messages to logs
    """
    
    def __init__(self, request: Any):
        """
        Initialize log printer
        
        Args:
            request: Agent request object
        """
        self.request = request
    
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        digital_employee: Optional[str], 
        is_final: bool
    ) -> None:
        """
        Send a message with full parameters to logs
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
            is_final: Whether this is the final message
        """
        if message_type == "deep_search":
            message = json.dumps(message) if not isinstance(message, str) else message
        
        request_id = getattr(self.request, 'request_id', 'unknown')
        logger.info(f"{request_id} {message_id} {message_type} {message} {digital_employee} {is_final}")
    
    def send(self, message_type: str, message: Any) -> None:
        """
        Send a message with minimal parameters to logs
        
        Args:
            message_type: Type of the message
            message: Message content
        """
        self.send(None, message_type, message, None, True)
    
    def send(self, message_type: str, message: Any, digital_employee: Optional[str]) -> None:
        """
        Send a message with digital employee to logs
        
        Args:
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
        """
        self.send(None, message_type, message, digital_employee, True)
    
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        is_final: bool
    ) -> None:
        """
        Send a message with message ID and final flag to logs
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            is_final: Whether this is the final message
        """
        self.send(message_id, message_type, message, None, is_final)
    
    def close(self) -> None:
        """
        Close the log printer (no-op for log printer)
        """
        pass
    
    def update_agent_type(self, agent_type: AgentType) -> None:
        """
        Update the agent type (no-op for log printer)
        
        Args:
            agent_type: New agent type
        """
        pass