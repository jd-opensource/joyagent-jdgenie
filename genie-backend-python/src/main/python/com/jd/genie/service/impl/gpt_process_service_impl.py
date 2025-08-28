"""
GPT process service implementation.
"""

import logging
from typing import Optional

from fastapi.responses import StreamingResponse

from ..i_gpt_process_service import IGptProcessService
from ..i_multi_agent_service import IMultiAgentService
from ...model.req.gpt_query_req import GptQueryReq
from ...util.chatei_utils import ChateiUtils
from ...util.sse_util import SseUtil

logger = logging.getLogger(__name__)


class GptProcessServiceImpl(IGptProcessService):
    """Implementation of GPT process service."""
    
    def __init__(self, multi_agent_service: IMultiAgentService):
        """
        Initialize with multi-agent service dependency.
        
        Args:
            multi_agent_service: Multi-agent service instance
        """
        self.multi_agent_service = multi_agent_service
    
    async def query_multi_agent_incr_stream(self, req: GptQueryReq) -> StreamingResponse:
        """
        Process multi-agent incremental stream query.
        
        Args:
            req: GPT query request
            
        Returns:
            Streaming response for SSE
        """
        timeout_millis = 3600000  # 1 hour in milliseconds
        req.user = "genie"
        req.deep_think = req.deep_think if req.deep_think is not None else 0
        
        trace_id = ChateiUtils.get_request_id(req)
        req.trace_id = trace_id
        
        emitter = SseUtil.build(timeout_millis, req.trace_id)
        
        # Start the multi-agent processing asynchronously
        await self.multi_agent_service.search_for_agent_request(req, emitter)
        
        logger.info(f"queryMultiAgentIncrStream GptQueryReq request: {req}")
        return emitter