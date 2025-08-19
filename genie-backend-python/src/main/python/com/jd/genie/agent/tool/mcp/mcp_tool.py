"""
MCP (Model Context Protocol) tool for calling external MCP servers.
MCP工具用于调用外部MCP服务器
"""
import json
import logging
from typing import Any, Dict, Optional
from dataclasses import dataclass

from ..base_tool import BaseTool
from ...util.http_util import HttpUtil
from ...util.dependency_container import DependencyContainer

logger = logging.getLogger(__name__)


@dataclass
class McpToolRequest:
    """MCP tool request data class."""
    server_url: str
    name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None


@dataclass
class McpToolResponse:
    """MCP tool response data class."""
    code: str
    message: str
    data: str


class McpTool(BaseTool):
    """MCP tool for calling external MCP servers."""
    
    def __init__(self):
        self.agent_context = None
    
    def get_name(self) -> str:
        return "mcp_tool"
    
    def get_description(self) -> str:
        return ""
    
    def to_params(self) -> Dict[str, Any]:
        return {}
    
    def execute(self, input_data: Any) -> Any:
        return None
    
    def list_tool(self, mcp_server_url: str) -> str:
        """List available tools from MCP server."""
        try:
            config = DependencyContainer.get_config()
            mcp_client_url = f"{config.mcp_client_url}/v1/tool/list"
            
            mcp_tool_request = McpToolRequest(server_url=mcp_server_url)
            request_data = {
                "server_url": mcp_tool_request.server_url
            }
            
            response = HttpUtil.post_json(mcp_client_url, json.dumps(request_data), None, 30)
            logger.info(f"list tool request: {json.dumps(request_data)} response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"{self.agent_context.request_id if self.agent_context else 'unknown'} list tool error", exc_info=e)
        return ""
    
    def call_tool(self, mcp_server_url: str, tool_name: str, input_data: Any) -> str:
        """Call a specific tool on the MCP server."""
        try:
            config = DependencyContainer.get_config()
            mcp_client_url = f"{config.mcp_client_url}/v1/tool/call"
            
            params = input_data if isinstance(input_data, dict) else {}
            
            mcp_tool_request = McpToolRequest(
                name=tool_name,
                server_url=mcp_server_url,
                arguments=params
            )
            
            request_data = {
                "name": mcp_tool_request.name,
                "server_url": mcp_tool_request.server_url,
                "arguments": mcp_tool_request.arguments
            }
            
            response = HttpUtil.post_json(mcp_client_url, json.dumps(request_data), None, 30)
            logger.info(f"call tool request: {json.dumps(request_data)} response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"{self.agent_context.request_id if self.agent_context else 'unknown'} call tool error", exc_info=e)
        return ""
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context