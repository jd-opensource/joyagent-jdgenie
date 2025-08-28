"""
Multi-agent service implementation.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi.responses import StreamingResponse

from ..i_multi_agent_service import IMultiAgentService
from ...agent.enums.agent_type import AgentType
from ...agent.enums.auto_bots_result_status import AutoBotsResultStatus
from ...agent.enums.response_type_enum import ResponseTypeEnum
from ...config.genie_config import GenieConfig
from ...handler.agent_response_handler import AgentResponseHandler
from ...model.dto.auto_bots_result import AutoBotsResult
from ...model.multi.event_result import EventResult
from ...model.req.agent_request import AgentRequest
from ...model.req.gpt_query_req import GptQueryReq
from ...model.response.agent_response import AgentResponse
from ...model.response.gpt_process_result import GptProcessResult
from ...util.chatei_utils import ChateiUtils

logger = logging.getLogger(__name__)


class MultiAgentServiceImpl(IMultiAgentService):
    """Implementation of multi-agent service."""
    
    def __init__(
        self, 
        genie_config: GenieConfig,
        handler_map: Dict[AgentType, AgentResponseHandler]
    ):
        """
        Initialize with dependencies.
        
        Args:
            genie_config: Genie configuration
            handler_map: Map of agent types to their handlers
        """
        self.genie_config = genie_config
        self.handler_map = handler_map
    
    async def search_for_agent_request(
        self, 
        gpt_query_req: GptQueryReq, 
        streaming_response: StreamingResponse
    ) -> AutoBotsResult:
        """
        Process agent request with streaming response.
        
        Args:
            gpt_query_req: GPT query request
            streaming_response: Streaming response for SSE
            
        Returns:
            AutoBots result
        """
        agent_request = self._build_agent_request(gpt_query_req)
        logger.info(f"{gpt_query_req.request_id} start handle Agent request: {json.dumps(agent_request.__dict__)}")
        
        try:
            await self._handle_multi_agent_request(agent_request, streaming_response)
        except Exception as e:
            logger.error(
                f"{gpt_query_req.request_id}, error in requestMultiAgent, "
                f"deepThink: {gpt_query_req.deep_think}, errorMsg: {str(e)}", 
                exc_info=e
            )
            raise e
        finally:
            logger.info(
                f"{gpt_query_req.request_id}, agent.query.web.singleRequest end, "
                f"requestId: {json.dumps(gpt_query_req.__dict__)}"
            )
        
        return ChateiUtils.to_auto_bots_result(agent_request, AutoBotsResultStatus.LOADING.name)
    
    async def _handle_multi_agent_request(
        self, 
        auto_req: AgentRequest, 
        streaming_response: StreamingResponse
    ) -> None:
        """
        Handle multi-agent request with HTTP streaming.
        
        Args:
            auto_req: Agent request
            streaming_response: Streaming response for SSE
        """
        start_time = time.time() * 1000  # Convert to milliseconds
        
        # Build HTTP request
        url = "http://127.0.0.1:8080/AutoAgent"
        headers = {"Content-Type": "application/json"}
        data = json.dumps(auto_req.__dict__)
        
        logger.info(f"{auto_req.request_id} agentRequest: {data}")
        
        timeout = httpx.Timeout(
            connect=60.0,
            read=self.genie_config.sse_client_read_timeout,
            write=1800.0,
            pool=self.genie_config.sse_client_connect_timeout
        )
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                async with client.stream("POST", url, headers=headers, content=data) as response:
                    await self._process_stream_response(
                        response, auto_req, streaming_response, start_time
                    )
            except Exception as e:
                logger.error(f"Request failed: {str(e)}", exc_info=e)
                raise
    
    async def _process_stream_response(
        self,
        response: httpx.Response,
        auto_req: AgentRequest,
        streaming_response: StreamingResponse,
        start_time: float
    ) -> None:
        """
        Process streaming response from the agent service.
        
        Args:
            response: HTTP response stream
            auto_req: Agent request
            streaming_response: Streaming response for SSE
            start_time: Request start time in milliseconds
        """
        agent_resp_list: List[AgentResponse] = []
        event_result = EventResult()
        
        if not response.is_success:
            error_content = await response.aread()
            logger.error(f"{auto_req.request_id}, response body is failed: {error_content.decode()}")
            return
        
        async for line_bytes in response.aiter_lines():
            line = line_bytes.decode('utf-8')
            
            if not line.startswith("data:"):
                continue
            
            data = line[5:]  # Remove "data:" prefix
            
            if data == "[DONE]":
                logger.info(f"{auto_req.request_id} data equals with [DONE]: {data}")
                break
            
            if data.startswith("heartbeat"):
                result = self._build_heartbeat_data(auto_req.request_id)
                await streaming_response.send(json.dumps(result.__dict__))
                logger.info(f"{auto_req.request_id} heartbeat-data: {data}")
                continue
            
            logger.info(f"{auto_req.request_id} recv from autocontroller: {data}")
            
            try:
                agent_response = AgentResponse(**json.loads(data))
                agent_type = AgentType.from_code(auto_req.agent_type)
                handler = self.handler_map.get(agent_type)
                
                if handler:
                    result = await handler.handle(auto_req, agent_response, agent_resp_list, event_result)
                    if result:
                        await streaming_response.send(json.dumps(result.__dict__))
                        
                        if result.finished:
                            # Record task execution time
                            total_time = time.time() * 1000 - start_time
                            logger.info(f"{auto_req.request_id} task total cost time: {total_time}ms")
                            break
                            
            except Exception as e:
                logger.error(f"Error processing stream data: {str(e)}", exc_info=e)
    
    def _build_agent_request(self, req: GptQueryReq) -> AgentRequest:
        """
        Build agent request from GPT query request.
        
        Args:
            req: GPT query request
            
        Returns:
            Agent request
        """
        request = AgentRequest()
        request.request_id = req.trace_id
        request.erp = req.user
        request.query = req.query
        request.agent_type = 5 if req.deep_think == 0 else 3
        
        if request.agent_type == 3:
            request.sop_prompt = self.genie_config.genie_sop_prompt
        else:
            request.sop_prompt = ""
            
        if request.agent_type == 5:
            request.base_prompt = self.genie_config.genie_base_prompt
        else:
            request.base_prompt = ""
            
        request.is_stream = True
        request.output_style = req.output_style
        
        return request
    
    def _build_heartbeat_data(self, request_id: str) -> GptProcessResult:
        """
        Build heartbeat data for SSE.
        
        Args:
            request_id: Request identifier
            
        Returns:
            GPT process result for heartbeat
        """
        result = GptProcessResult()
        result.finished = False
        result.status = "success"
        result.response_type = ResponseTypeEnum.TEXT.name
        result.response = ""
        result.response_all = ""
        result.use_times = 0
        result.use_tokens = 0
        result.req_id = request_id
        result.package_type = "heartbeat"
        result.encrypted = False
        
        return result