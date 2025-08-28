"""
Genie controller for handling agent requests.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.requests import Request

try:
    from ..agent.agent.agent_context import AgentContext
    from ..agent.enums.agent_type import AgentType
    from ..agent.printer.printer import Printer
    from ..agent.printer.sse_printer import SSEPrinter
    from ..agent.tool.tool_collection import ToolCollection
    from ..agent.tool.common.file_tool import FileTool
    from ..agent.tool.common.code_interpreter_tool import CodeInterpreterTool
    from ..agent.tool.common.report_tool import ReportTool
    from ..agent.tool.common.deep_search_tool import DeepSearchTool
    from ..agent.tool.mcp.mcp_tool import McpTool
    from ..agent.util.date_util import DateUtil
    from ..config.genie_config import GenieConfig
    from ..model.req.agent_request import AgentRequest
    from ..model.req.gpt_query_req import GptQueryReq
    from ..service.agent_handler_service import AgentHandlerService
    from ..service.i_gpt_process_service import IGptProcessService
    from ..service.impl.agent_handler_factory import AgentHandlerFactory
except ImportError:
    # Fallback to absolute imports if relative imports fail
    from com.jd.genie.agent.agent.agent_context import AgentContext
    from com.jd.genie.agent.enums.agent_type import AgentType
    from com.jd.genie.agent.printer.printer import Printer
    from com.jd.genie.agent.printer.sse_printer import SSEPrinter
    from com.jd.genie.agent.tool.tool_collection import ToolCollection
    from com.jd.genie.agent.tool.common.file_tool import FileTool
    from com.jd.genie.agent.tool.common.code_interpreter_tool import CodeInterpreterTool
    from com.jd.genie.agent.tool.common.report_tool import ReportTool
    from com.jd.genie.agent.tool.common.deep_search_tool import DeepSearchTool
    from com.jd.genie.agent.tool.mcp.mcp_tool import McpTool
    from com.jd.genie.agent.util.date_util import DateUtil
    from com.jd.genie.config.genie_config import GenieConfig
    from com.jd.genie.model.req.agent_request import AgentRequest
    from com.jd.genie.model.req.gpt_query_req import GptQueryReq
    from com.jd.genie.service.agent_handler_service import AgentHandlerService
    from com.jd.genie.service.i_gpt_process_service import IGptProcessService
    from com.jd.genie.service.impl.agent_handler_factory import AgentHandlerFactory

logger = logging.getLogger(__name__)

router = APIRouter()


class GenieController:
    """Controller for handling Genie agent requests."""
    
    HEARTBEAT_INTERVAL = 10.0  # 10 seconds heartbeat interval
    AUTO_AGENT_SSE_TIMEOUT = 3600.0  # 1 hour timeout
    
    def __init__(
        self,
        genie_config: GenieConfig,
        agent_handler_factory: AgentHandlerFactory,
        gpt_process_service: IGptProcessService
    ):
        """
        Initialize the controller.
        
        Args:
            genie_config: Genie configuration
            agent_handler_factory: Agent handler factory
            gpt_process_service: GPT process service
        """
        self.genie_config = genie_config
        self.agent_handler_factory = agent_handler_factory
        self.gpt_process_service = gpt_process_service
    
    async def start_heartbeat(self, stream: StreamingResponse, request_id: str) -> asyncio.Task:
        """
        Start SSE heartbeat.
        
        Args:
            stream: SSE stream
            request_id: Request identifier
            
        Returns:
            Heartbeat task
        """
        async def heartbeat_loop():
            while True:
                try:
                    await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                    logger.info(f"{request_id} send heartbeat")
                    await stream.send("heartbeat")
                except Exception as e:
                    logger.error(f"{request_id} heartbeat failed, closing connection", exc_info=e)
                    break
        
        return asyncio.create_task(heartbeat_loop())
    
    def handle_output_style(self, request: AgentRequest) -> str:
        """
        Handle output style for the query.
        
        HTML mode: query + display as html
        Docs mode: query + display as markdown
        Table mode: query + display as excel
        
        Args:
            request: Agent request
            
        Returns:
            Modified query with output style
        """
        query = request.query
        output_style_map = self.genie_config.get_output_style_prompts()
        
        if request.output_style:
            style_prompt = output_style_map.get(request.output_style, "")
            query += style_prompt
            
        return query
    
    async def build_tool_collection(
        self, 
        agent_context: AgentContext, 
        request: AgentRequest
    ) -> ToolCollection:
        """
        Build tool collection for the agent.
        
        Args:
            agent_context: Agent context
            request: Agent request
            
        Returns:
            Configured tool collection
        """
        tool_collection = ToolCollection()
        tool_collection.agent_context = agent_context
        
        # Add file tool
        file_tool = FileTool()
        file_tool.agent_context = agent_context
        tool_collection.add_tool(file_tool)
        
        # Add default tools based on configuration
        tool_list_map = self.genie_config.get_multi_agent_tool_list_map()
        default_tools = tool_list_map.get("default", "search,code,report").split(",")
        
        if default_tools:
            if "code" in default_tools:
                code_tool = CodeInterpreterTool()
                code_tool.agent_context = agent_context
                tool_collection.add_tool(code_tool)
                
            if "report" in default_tools:
                report_tool = ReportTool()
                report_tool.agent_context = agent_context
                tool_collection.add_tool(report_tool)
                
            if "search" in default_tools:
                deep_search_tool = DeepSearchTool()
                deep_search_tool.agent_context = agent_context
                tool_collection.add_tool(deep_search_tool)
        
        # Add MCP tools
        try:
            mcp_tool = McpTool()
            mcp_tool.agent_context = agent_context
            
            for mcp_server in self.genie_config.get_mcp_server_url_arr():
                list_tool_result = await mcp_tool.list_tool(mcp_server)
                if not list_tool_result:
                    logger.error(f"{agent_context.request_id} mcp server {mcp_server} invalid")
                    continue
                
                try:
                    resp = json.loads(list_tool_result)
                    if resp.get("code") != 200:
                        logger.error(
                            f"{agent_context.request_id} mcp serve {mcp_server} "
                            f"code: {resp.get('code')}, message: {resp.get('message')}"
                        )
                        continue
                    
                    data = resp.get("data", [])
                    if not data:
                        logger.error(
                            f"{agent_context.request_id} mcp serve {mcp_server} "
                            f"code: {resp.get('code')}, message: {resp.get('message')}"
                        )
                        continue
                    
                    for tool_info in data:
                        method = tool_info.get("name")
                        description = tool_info.get("description") 
                        input_schema = tool_info.get("inputSchema")
                        tool_collection.add_mcp_tool(method, description, input_schema, mcp_server)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse MCP response: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"{agent_context.request_id} add mcp tool failed", exc_info=e)
        
        return tool_collection


# Dependency injection functions
def get_app_state(request: Request):
    """Get app state from request."""
    return request.app.state


def get_genie_config(request: Request) -> GenieConfig:
    """Get Genie configuration dependency."""
    return request.app.state.config


def get_agent_handler_factory(request: Request) -> AgentHandlerFactory:
    """Get agent handler factory dependency."""
    return request.app.state.agent_handler_factory


def get_gpt_process_service(request: Request) -> IGptProcessService:
    """Get GPT process service dependency."""
    return request.app.state.gpt_process_service


def get_genie_controller(request: Request) -> GenieController:
    """Get Genie controller dependency."""
    app_state = request.app.state
    return GenieController(
        app_state.config,
        app_state.agent_handler_factory,
        app_state.gpt_process_service
    )


@router.post("/AutoAgent")
async def auto_agent(
    agent_request: AgentRequest,
    request: Request
) -> StreamingResponse:
    """
    Execute agent scheduling.
    
    Args:
        agent_request: Agent request
        request: FastAPI request for dependency injection
        
    Returns:
        SSE streaming response
    """
    controller = get_genie_controller(request)
    logger.info(f"{agent_request.request_id} auto agent request: {json.dumps(agent_request.dict())}")
    
    async def generate():
        try:
            # Create SSE printer
            printer = SSEPrinter(agent_request, agent_request.agent_type)
            
            # Build agent context
            agent_context = AgentContext(
                request_id=agent_request.request_id,
                session_id=agent_request.request_id,
                printer=printer,
                query=controller.handle_output_style(agent_request),
                task="",
                date_info=DateUtil.current_date_info(),
                product_files=[],
                task_product_files=[],
                sop_prompt=agent_request.sop_prompt,
                base_prompt=agent_request.base_prompt,
                agent_type=agent_request.agent_type,
                is_stream=agent_request.is_stream if agent_request.is_stream is not None else False
            )
            
            # Build tool collection
            agent_context.tool_collection = await controller.build_tool_collection(agent_context, agent_request)
            
            # Get appropriate handler
            handler = controller.agent_handler_factory.get_handler(agent_context, agent_request)
            
            if handler:
                # Execute processing logic
                await handler.handle(agent_context, agent_request)
            else:
                logger.error(f"{agent_request.request_id} No suitable handler found")
                yield "data: {'error': 'No suitable handler found'}\n\n"
                
        except Exception as e:
            logger.error(f"{agent_request.request_id} auto agent error", exc_info=e)
            yield f"data: {{'error': '{str(e)}'}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/web/health")
async def health() -> PlainTextResponse:
    """
    Health check endpoint.
    
    Returns:
        Health status response
    """
    return PlainTextResponse("ok")


@router.post("/web/api/v1/gpt/queryAgentStreamIncr")
async def query_agent_stream_incr(
    params: GptQueryReq,
    request: Request
) -> StreamingResponse:
    """
    Handle Agent streaming incremental query requests, return SSE event stream.
    
    Args:
        params: Query request parameters containing GPT query information
        request: FastAPI request for dependency injection
        
    Returns:
        SSE event stream for streaming incremental response results
    """
    controller = get_genie_controller(request)
    return await controller.gpt_process_service.query_multi_agent_incr_stream(params)