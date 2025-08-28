"""
智能体类型枚举
"""
from enum import Enum


class IsDefaultAgent(Enum):
    """是否为默认智能体枚举"""
    IS_DEFAULT_AGENT = 1      # 是默认智能体
    NOT_DEFAULT_AGENT = 2     # 不是默认智能体

    def get_value(self) -> int:
        """获取枚举值"""
        return self.value

    @classmethod
    def from_value(cls, value: int) -> "IsDefaultAgent":
        """根据值获取枚举实例"""
        for item in cls:
            if item.value == value:
                return item
        raise ValueError(f"Invalid IsDefaultAgent value: {value}")

    def is_default(self) -> bool:
        """判断是否为默认智能体"""
        return self == IsDefaultAgent.IS_DEFAULT_AGENT