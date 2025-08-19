"""
Agent response handler interface.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..model.multi.event_result import EventResult
from ..model.req.agent_request import AgentRequest
from ..model.response.agent_response import AgentResponse
from ..model.response.gpt_process_result import GptProcessResult


class AgentResponseHandler(ABC):
    """Abstract base class for agent response handlers."""
    
    @abstractmethod
    async def handle(
        self,
        request: AgentRequest,
        response: AgentResponse,
        agent_resp_list: List[AgentResponse],
        event_result: EventResult
    ) -> Optional[GptProcessResult]:
        """
        Handle agent response processing.
        
        Args:
            request: The agent request
            response: The agent response
            agent_resp_list: List of agent responses
            event_result: Event result object
            
        Returns:
            Processed GPT result or None
        """
        pass