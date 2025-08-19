"""
Token 数量超出限制异常
"""
from enum import Enum
from typing import Optional


class MessageType(Enum):
    """消息类型枚举"""
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    TOOL = "TOOL"
    UNKNOWN = "UNKNOWN"


class TokenLimitExceeded(RuntimeError):
    """Token 数量超出限制异常"""

    def __init__(
        self,
        message: Optional[str] = None,
        current_tokens: int = 0,
        max_tokens: int = 0,
        message_type: MessageType = MessageType.UNKNOWN
    ):
        """
        构造函数
        
        Args:
            message: 自定义错误消息
            current_tokens: 当前token数量
            max_tokens: 最大允许token数量
            message_type: 消息类型
        """
        if message is None:
            if current_tokens > 0 and max_tokens > 0:
                exceeded = current_tokens - max_tokens
                message = (
                    f"Token limit exceeded: current={current_tokens}, "
                    f"max={max_tokens}, exceeded={exceeded}, "
                    f"messageType={message_type.value}"
                )
            else:
                message = "Token limit exceeded"
        
        super().__init__(message)
        
        self._current_tokens = current_tokens
        self._max_tokens = max_tokens
        self._message_type = message_type

    @property
    def current_tokens(self) -> int:
        """获取当前 token 数量"""
        return self._current_tokens

    @property
    def max_tokens(self) -> int:
        """获取最大允许 token 数量"""
        return self._max_tokens

    @property
    def exceeded_tokens(self) -> int:
        """获取超出限制的 token 数量"""
        return self._current_tokens - self._max_tokens

    @property
    def message_type(self) -> MessageType:
        """获取消息类型"""
        return self._message_type

    def __str__(self) -> str:
        """返回异常的字符串表示"""
        return super().__str__()

    def __repr__(self) -> str:
        """返回异常的开发者表示"""
        return (
            f"TokenLimitExceeded(current_tokens={self._current_tokens}, "
            f"max_tokens={self._max_tokens}, "
            f"message_type={self._message_type.value})"
        )