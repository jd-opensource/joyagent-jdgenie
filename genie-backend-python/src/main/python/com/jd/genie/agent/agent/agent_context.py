"""
Agent Context - Contains the context and configuration for agent execution
"""
from typing import List, Optional
from dataclasses import dataclass, field
import logging

from com.jd.genie.agent.dto.file import File
from com.jd.genie.agent.printer.printer import Printer
from com.jd.genie.agent.tool.tool_collection import ToolCollection

logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """
    代理上下文 - 包含代理执行所需的上下文和配置信息
    """
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    query: Optional[str] = None
    task: Optional[str] = None
    printer: Optional[Printer] = None
    tool_collection: Optional[ToolCollection] = None
    date_info: Optional[str] = None
    product_files: List[File] = field(default_factory=list)
    is_stream: Optional[bool] = None
    stream_message_type: Optional[str] = None
    sop_prompt: Optional[str] = None
    base_prompt: Optional[str] = None
    agent_type: Optional[int] = None
    task_product_files: List[File] = field(default_factory=list)

    def __post_init__(self):
        """Initialize after creation"""
        if self.product_files is None:
            self.product_files = []
        if self.task_product_files is None:
            self.task_product_files = []

    @classmethod
    def builder(cls):
        """Builder pattern implementation"""
        return cls()

    def set_request_id(self, request_id: str) -> 'AgentContext':
        """Set request ID"""
        self.request_id = request_id
        return self

    def set_session_id(self, session_id: str) -> 'AgentContext':
        """Set session ID"""
        self.session_id = session_id
        return self

    def set_query(self, query: str) -> 'AgentContext':
        """Set query"""
        self.query = query
        return self

    def set_task(self, task: str) -> 'AgentContext':
        """Set task"""
        self.task = task
        return self

    def set_printer(self, printer: Printer) -> 'AgentContext':
        """Set printer"""
        self.printer = printer
        return self

    def set_tool_collection(self, tool_collection: ToolCollection) -> 'AgentContext':
        """Set tool collection"""
        self.tool_collection = tool_collection
        return self

    def set_date_info(self, date_info: str) -> 'AgentContext':
        """Set date information"""
        self.date_info = date_info
        return self

    def set_product_files(self, product_files: List[File]) -> 'AgentContext':
        """Set product files"""
        self.product_files = product_files if product_files else []
        return self

    def set_is_stream(self, is_stream: bool) -> 'AgentContext':
        """Set stream flag"""
        self.is_stream = is_stream
        return self

    def set_stream_message_type(self, stream_message_type: str) -> 'AgentContext':
        """Set stream message type"""
        self.stream_message_type = stream_message_type
        return self

    def set_sop_prompt(self, sop_prompt: str) -> 'AgentContext':
        """Set SOP prompt"""
        self.sop_prompt = sop_prompt
        return self

    def set_base_prompt(self, base_prompt: str) -> 'AgentContext':
        """Set base prompt"""
        self.base_prompt = base_prompt
        return self

    def set_agent_type(self, agent_type: int) -> 'AgentContext':
        """Set agent type"""
        self.agent_type = agent_type
        return self

    def set_task_product_files(self, task_product_files: List[File]) -> 'AgentContext':
        """Set task product files"""
        self.task_product_files = task_product_files if task_product_files else []
        return self

    def get_request_id(self) -> Optional[str]:
        """Get request ID"""
        return self.request_id

    def get_session_id(self) -> Optional[str]:
        """Get session ID"""
        return self.session_id

    def get_query(self) -> Optional[str]:
        """Get query"""
        return self.query

    def get_task(self) -> Optional[str]:
        """Get task"""
        return self.task

    def get_printer(self) -> Optional[Printer]:
        """Get printer"""
        return self.printer

    def get_tool_collection(self) -> Optional[ToolCollection]:
        """Get tool collection"""
        return self.tool_collection

    def get_date_info(self) -> Optional[str]:
        """Get date information"""
        return self.date_info

    def get_product_files(self) -> List[File]:
        """Get product files"""
        return self.product_files if self.product_files else []

    def get_is_stream(self) -> Optional[bool]:
        """Get stream flag"""
        return self.is_stream

    def get_stream_message_type(self) -> Optional[str]:
        """Get stream message type"""
        return self.stream_message_type

    def get_sop_prompt(self) -> Optional[str]:
        """Get SOP prompt"""
        return self.sop_prompt

    def get_base_prompt(self) -> Optional[str]:
        """Get base prompt"""
        return self.base_prompt

    def get_agent_type(self) -> Optional[int]:
        """Get agent type"""
        return self.agent_type

    def get_task_product_files(self) -> List[File]:
        """Get task product files"""
        return self.task_product_files if self.task_product_files else []