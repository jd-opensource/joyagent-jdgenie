"""
Agent handler configuration.
"""

from typing import Dict, List
from ..agent.enums.agent_type import AgentType
from .agent_response_handler import AgentResponseHandler
from .plan_solve_agent_response_handler import PlanSolveAgentResponseHandler
from .react_agent_response_handler import ReactAgentResponseHandler


class AgentHandlerConfig:
    """Configuration for agent handlers providing handler mapping."""
    
    def __init__(self, handler_list: List[AgentResponseHandler]):
        """
        Initialize handler configuration.
        
        Args:
            handler_list: List of agent response handlers
        """
        self.handler_list = handler_list
        self._handler_map: Dict[AgentType, AgentResponseHandler] = {}
        self._build_handler_map()
    
    def _build_handler_map(self) -> None:
        """Build the handler map from the handler list."""
        for handler in self.handler_list:
            if isinstance(handler, PlanSolveAgentResponseHandler):
                self._handler_map[AgentType.PLAN_SOLVE] = handler
            elif isinstance(handler, ReactAgentResponseHandler):
                self._handler_map[AgentType.REACT] = handler
            # Extensible for more handlers
    
    def get_handler_map(self) -> Dict[AgentType, AgentResponseHandler]:
        """
        Get the handler map.
        
        Returns:
            Dictionary mapping agent types to their handlers
        """
        return self._handler_map.copy()
    
    def get_handler(self, agent_type: AgentType) -> AgentResponseHandler:
        """
        Get handler for specific agent type.
        
        Args:
            agent_type: The agent type
            
        Returns:
            The corresponding handler
            
        Raises:
            KeyError: If no handler found for the agent type
        """
        if agent_type not in self._handler_map:
            raise KeyError(f"No handler found for agent type: {agent_type}")
        return self._handler_map[agent_type]