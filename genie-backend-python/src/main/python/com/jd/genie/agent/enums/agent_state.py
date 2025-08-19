"""
代理状态枚举
"""
from enum import Enum


class AgentState(Enum):
    """代理状态枚举"""
    IDLE = "IDLE"          # 空闲状态
    RUNNING = "RUNNING"    # 运行状态
    FINISHED = "FINISHED"  # 完成状态
    ERROR = "ERROR"        # 错误状态

    def __str__(self) -> str:
        """返回枚举值的字符串表示"""
        return self.value