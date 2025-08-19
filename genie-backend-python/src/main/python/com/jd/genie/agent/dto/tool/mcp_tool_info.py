"""
MCP工具信息
"""
from typing import Optional
from pydantic import BaseModel, Field


class McpToolInfo(BaseModel):
    """MCP工具信息"""
    mcp_server_url: Optional[str] = Field(None, description="MCP服务器URL")
    name: Optional[str] = Field(None, description="工具名称")
    desc: Optional[str] = Field(None, description="工具描述")
    parameters: Optional[str] = Field(None, description="工具参数")