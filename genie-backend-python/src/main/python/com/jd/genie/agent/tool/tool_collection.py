"""
Tool collection class for managing available tools.
工具集合类 - 管理可用的工具
"""
import logging
from typing import Any, Dict, Optional

from .base_tool import BaseTool
from .mcp.mcp_tool import McpTool
from ..dto.tool.mcp_tool_info import McpToolInfo

logger = logging.getLogger(__name__)


class ToolCollection:
    """Tool collection class for managing available tools."""
    
    def __init__(self):
        self.tool_map: Dict[str, BaseTool] = {}
        self.mcp_tool_map: Dict[str, McpToolInfo] = {}
        self.agent_context = None
        
        # 数字员工列表
        # task未并发的情况下
        # 1、每一个task，执行时，数字员工列表就会更新
        # TODO 并发情况下需要处理
        self.current_task: Optional[str] = None
        self.digital_employees: Optional[Dict[str, Any]] = None
    
    def add_tool(self, tool: BaseTool) -> None:
        """添加工具"""
        self.tool_map[tool.get_name()] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tool_map.get(name)
    
    def add_mcp_tool(self, name: str, desc: str, parameters: str, mcp_server_url: str) -> None:
        """添加MCP工具"""
        self.mcp_tool_map[name] = McpToolInfo(
            name=name,
            desc=desc,
            parameters=parameters,
            mcp_server_url=mcp_server_url
        )
    
    def get_mcp_tool(self, name: str) -> Optional[McpToolInfo]:
        """获取MCP工具"""
        return self.mcp_tool_map.get(name)
    
    def execute(self, name: str, tool_input: Any) -> Any:
        """执行工具"""
        if name in self.tool_map:
            tool = self.get_tool(name)
            return tool.execute(tool_input)
        elif name in self.mcp_tool_map:
            tool_info = self.mcp_tool_map[name]
            mcp_tool = McpTool()
            mcp_tool.set_agent_context(self.agent_context)
            return mcp_tool.call_tool(tool_info.mcp_server_url, name, tool_input)
        else:
            logger.error(f"Error: Unknown tool {name}")
        return None
    
    def update_digital_employee(self, digital_employee: Dict[str, Any]) -> None:
        """设置数字员工"""
        if digital_employee is None:
            logger.error(f"requestId:{self.agent_context.request_id if self.agent_context else 'unknown'} setDigitalEmployee: {digital_employee}")
        self.digital_employees = digital_employee
    
    def get_digital_employee(self, tool_name: str) -> Optional[str]:
        """获取数字员工名称"""
        if not tool_name:
            return None
        
        if self.digital_employees is None:
            return None
        
        return self.digital_employees.get(tool_name)
    
    # Properties for compatibility
    @property
    def current_task(self) -> Optional[str]:
        return getattr(self, '_current_task', None)
    
    @current_task.setter
    def current_task(self, value: Optional[str]) -> None:
        self._current_task = value