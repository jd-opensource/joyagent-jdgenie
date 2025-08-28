"""
响应类型枚举
"""
from enum import Enum


class ResponseTypeEnum(Enum):
    """响应类型枚举"""
    MARKDOWN = "markdown"
    TEXT = "text"
    CARD = "card"

    def __str__(self) -> str:
        """返回枚举值的字符串表示"""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "ResponseTypeEnum":
        """从字符串获取响应类型"""
        for response_type in cls:
            if response_type.value == value:
                return response_type
        raise ValueError(f"Invalid ResponseTypeEnum value: {value}")

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """检查响应类型值是否有效"""
        return any(response_type.value == value for response_type in cls)