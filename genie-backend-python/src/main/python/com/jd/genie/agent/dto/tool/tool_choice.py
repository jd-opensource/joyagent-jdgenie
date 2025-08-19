"""
工具选择类型枚举
"""
from enum import Enum
from typing import Set


class ToolChoice(Enum):
    """工具选择类型枚举"""
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"

    @classmethod
    def get_valid_values(cls) -> Set[str]:
        """获取所有有效的工具选择值"""
        return {choice.value for choice in cls}

    @classmethod
    def is_valid(cls, tool_choice: "ToolChoice") -> bool:
        """检查工具选择值是否有效"""
        return tool_choice is not None and tool_choice.value in cls.get_valid_values()

    @classmethod
    def from_string(cls, tool_choice: str) -> "ToolChoice":
        """从字符串获取工具选择类型"""
        for choice in cls:
            if choice.value == tool_choice:
                return choice
        raise ValueError(f"Invalid tool choice: {tool_choice}")