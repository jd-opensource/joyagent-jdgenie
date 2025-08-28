"""
记忆类 - 管理代理的消息历史
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from ..enums.role_type import RoleType
from .message import Message


class Memory(BaseModel):
    """记忆类 - 管理代理的消息历史"""
    messages: List[Message] = Field(default_factory=list, description="消息列表")

    def add_message(self, message: Message) -> None:
        """添加消息"""
        self.messages.append(message)

    def add_messages(self, new_messages: List[Message]) -> None:
        """添加多条消息"""
        self.messages.extend(new_messages)

    def get_last_message(self) -> Optional[Message]:
        """获取最后一条消息"""
        return self.messages[-1] if self.messages else None

    def clear(self) -> None:
        """清空记忆"""
        self.messages.clear()

    def clear_tool_context(self) -> None:
        """清空工具执行历史"""
        self.messages = [
            message for message in self.messages
            if not (
                message.role == RoleType.TOOL or
                (message.role == RoleType.ASSISTANT and 
                 message.tool_calls is not None and 
                 len(message.tool_calls) > 0) or
                (message.content is not None and 
                 message.content.startswith("根据当前状态和可用工具，确定下一步行动"))
            )
        ]

    def get_format_message(self) -> str:
        """格式化Message"""
        result = []
        for message in self.messages:
            result.append(f"role:{message.role.value if message.role else None} content:{message.content}")
        return "\n".join(result)

    def size(self) -> int:
        """获取消息数量"""
        return len(self.messages)

    def is_empty(self) -> bool:
        """检查是否为空"""
        return len(self.messages) == 0

    def get(self, index: int) -> Message:
        """根据索引获取消息"""
        return self.messages[index]