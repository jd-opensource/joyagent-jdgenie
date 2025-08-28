"""
Agent handler factory implementation.
"""

import logging
from typing import Dict, List, Optional

from ..agent_handler_service import AgentHandlerService
from ...agent.agent.agent_context import AgentContext
from ...model.req.agent_request import AgentRequest

logger = logging.getLogger(__name__)


class AgentHandlerFactory:
    """Factory for agent handlers."""
    
    def __init__(self, handlers: List[AgentHandlerService]):
        """
        Initialize the factory with handler list.
        
        Args:
            handlers: List of agent handler services
        """
        self.handler_map: Dict[str, AgentHandlerService] = {}
        
        # Initialize handler mapping
        for handler in handlers:
            # Register handlers by their class name (lowercase)
            handler_name = handler.__class__.__name__.lower()
            self.handler_map[handler_name] = handler
    
    def get_handler(
        self, 
        context: AgentContext, 
        request: AgentRequest
    ) -> Optional[AgentHandlerService]:
        """
        Get handler based on context and request.
        
        Args:
            context: Agent context
            request: Agent request
            
        Returns:
            Appropriate handler or None if not found
        """
        if context is None or request is None:
            return None
        
        # Method 1: Match using support method
        for handler in self.handler_map.values():
            if handler.support(context, request):
                return handler
        
        return None