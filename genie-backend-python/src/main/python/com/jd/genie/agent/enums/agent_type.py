"""
智能体类型枚举
"""
from enum import Enum
from typing import Optional


class AgentType(Enum):
    """智能体类型枚举"""
    COMPREHENSIVE = 1
    WORKFLOW = 2
    PLAN_SOLVE = 3
    ROUTER = 4
    REACT = 5

    def get_value(self) -> int:
        """获取枚举值"""
        return self.value

    @classmethod
    def from_code(cls, value: int) -> "AgentType":
        """根据代码值获取智能体类型"""
        for agent_type in cls:
            if agent_type.value == value:
                return agent_type
        raise ValueError(f"Invalid AgentType code: {value}")

    @classmethod
    def from_code_safe(cls, value: int) -> Optional["AgentType"]:
        """安全地根据代码值获取智能体类型，如果无效则返回None"""
        try:
            return cls.from_code(value)
        except ValueError:
            return None