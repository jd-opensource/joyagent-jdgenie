"""
GPT process service interface.
"""

from abc import ABC, abstractmethod
from fastapi.responses import StreamingResponse

from ..model.req.gpt_query_req import GptQueryReq


class IGptProcessService(ABC):
    """Interface for GPT processing services."""
    
    @abstractmethod
    async def query_multi_agent_incr_stream(self, req: GptQueryReq) -> StreamingResponse:
        """
        Single agent, multi-agent incremental interface.
        
        Args:
            req: GPT query request
            
        Returns:
            Streaming response for SSE
        """
        pass