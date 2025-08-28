"""
Plan solve agent response handler implementation.
"""

import logging
from typing import List, Optional

from .agent_response_handler import AgentResponseHandler
from .base_agent_response_handler import BaseAgentResponseHandler
from ..model.multi.event_result import EventResult
from ..model.req.agent_request import AgentRequest
from ..model.response.agent_response import AgentResponse
from ..model.response.gpt_process_result import GptProcessResult

logger = logging.getLogger(__name__)


class PlanSolveAgentResponseHandler(BaseAgentResponseHandler, AgentResponseHandler):
    """Handler for plan-solve agent responses."""
    
    async def handle(
        self,
        request: AgentRequest,
        response: AgentResponse,
        agent_resp_list: List[AgentResponse],
        event_result: EventResult
    ) -> Optional[GptProcessResult]:
        """
        Handle plan-solve agent response processing.
        
        Args:
            request: The agent request
            response: The agent response
            agent_resp_list: List of agent responses
            event_result: Event result object
            
        Returns:
            Processed GPT result or None
        """
        try:
            return self.build_incr_result(request, event_result, response)
        except Exception as e:
            logger.error(f"{request.request_id} PlanSolveAgentResponseHandler handle error", exc_info=e)
            return None