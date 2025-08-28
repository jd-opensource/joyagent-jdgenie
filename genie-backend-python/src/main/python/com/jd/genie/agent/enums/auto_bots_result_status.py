"""
AutoBots结果状态枚举
"""
from enum import Enum


class AutoBotsResultStatus(Enum):
    """AutoBots结果状态枚举"""
    LOADING = "loading"
    NO = "no"
    RUNNING = "running"
    ERROR = "error"
    FINISHED = "finished"

    def __str__(self) -> str:
        """返回枚举值的字符串表示"""
        return self.value