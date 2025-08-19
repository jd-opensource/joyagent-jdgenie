"""
消息角色类型枚举
"""
from enum import Enum
from typing import Set


class RoleType(Enum):
    """消息角色类型枚举"""
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"
    TOOL = "tool"

    @classmethod
    def get_valid_values(cls) -> Set[str]:
        """获取所有有效的角色值"""
        return {role.value for role in cls}

    @classmethod
    def is_valid(cls, role: str) -> bool:
        """检查角色值是否有效"""
        return role in cls.get_valid_values()

    @classmethod
    def from_string(cls, role: str) -> "RoleType":
        """从字符串获取角色类型"""
        for role_type in cls:
            if role_type.value == role:
                return role_type
        raise ValueError(f"Invalid role: {role}")