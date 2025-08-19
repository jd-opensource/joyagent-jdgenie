"""
Agent handler service interface.
"""

from abc import ABC, abstractmethod

from ..agent.agent.agent_context import AgentContext
from ..model.req.agent_request import AgentRequest


class AgentHandlerService(ABC):
    """Abstract base class for agent handler services."""
    
    @abstractmethod
    async def handle(self, context: AgentContext, request: AgentRequest) -> str:
        """
        Handle Agent request processing.
        
        Args:
            context: Agent context
            request: Agent request
            
        Returns:
            Processing result as string
        """
        pass
    
    @abstractmethod
    def support(self, context: AgentContext, request: AgentRequest) -> bool:
        """
        Check if this handler supports the given context and request.
        
        Args:
            context: Agent context
            request: Agent request
            
        Returns:
            True if this handler supports the request, False otherwise
        """
        pass