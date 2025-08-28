"""
消息类 - 表示代理系统中的各种消息
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from ..enums.role_type import RoleType
from .tool.tool_call import ToolCall


class Message(BaseModel):
    """消息类 - 表示代理系统中的各种消息"""
    role: Optional[RoleType] = Field(None, description="消息角色")
    content: Optional[str] = Field(None, description="消息内容")
    base64_image: Optional[str] = Field(None, description="图片数据（base64编码）")
    tool_call_id: Optional[str] = Field(None, description="工具调用ID")
    tool_calls: Optional[List[ToolCall]] = Field(None, description="工具调用列表")

    @classmethod
    def user_message(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        """创建用户消息"""
        return cls(
            role=RoleType.USER,
            content=content,
            base64_image=base64_image
        )

    @classmethod
    def system_message(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        """创建系统消息"""
        return cls(
            role=RoleType.SYSTEM,
            content=content,
            base64_image=base64_image
        )

    @classmethod
    def assistant_message(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        """创建助手消息"""
        return cls(
            role=RoleType.ASSISTANT,
            content=content,
            base64_image=base64_image
        )

    @classmethod
    def tool_message(cls, content: str, tool_call_id: str, base64_image: Optional[str] = None) -> "Message":
        """创建工具消息"""
        return cls(
            role=RoleType.TOOL,
            content=content,
            tool_call_id=tool_call_id,
            base64_image=base64_image
        )

    @classmethod
    def from_tool_calls(cls, content: str, tool_calls: List[ToolCall]) -> "Message":
        """从工具调用创建消息"""
        return cls(
            role=RoleType.ASSISTANT,
            content=content,
            tool_calls=tool_calls
        )