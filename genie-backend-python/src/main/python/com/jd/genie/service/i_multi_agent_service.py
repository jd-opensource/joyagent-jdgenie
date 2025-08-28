"""
Multi-agent service interface.
"""

from abc import ABC, abstractmethod
from fastapi.responses import StreamingResponse

from ..model.dto.auto_bots_result import AutoBotsResult
from ..model.req.gpt_query_req import GptQueryReq


class IMultiAgentService(ABC):
    """Interface for multi-agent services."""
    
    @abstractmethod
    async def search_for_agent_request(
        self, 
        gpt_query_req: GptQueryReq, 
        streaming_response: StreamingResponse
    ) -> AutoBotsResult:
        """
        Entry function for requesting multi-agent requests.
        
        Args:
            gpt_query_req: GPT query request
            streaming_response: Streaming response for SSE
            
        Returns:
            AutoBots result
        """
        pass