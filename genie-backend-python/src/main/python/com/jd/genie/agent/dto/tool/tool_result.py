"""
工具执行结果
"""
from enum import Enum
from typing import Any, Optional, TypeVar, Type
from pydantic import BaseModel, Field

T = TypeVar('T')


class ExecutionStatus(Enum):
    """执行状态枚举"""
    SUCCESS = "SUCCESS"      # 执行成功
    FAILED = "FAILED"        # 执行失败
    TIMEOUT = "TIMEOUT"      # 执行超时
    CANCELLED = "CANCELLED"  # 执行被取消
    SKIPPED = "SKIPPED"      # 执行被跳过


class ToolResult(BaseModel):
    """工具执行结果"""
    tool_name: Optional[str] = Field(None, description="工具名称")
    status: Optional[ExecutionStatus] = Field(None, description="执行状态")
    result: Optional[Any] = Field(None, description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: Optional[int] = Field(None, description="执行时间（毫秒）")
    parameters: Optional[Any] = Field(None, description="执行参数")

    @classmethod
    def success(cls, tool_name: str, result: Any, parameters: Optional[Any] = None) -> "ToolResult":
        """创建成功结果"""
        return cls(
            tool_name=tool_name,
            status=ExecutionStatus.SUCCESS,
            result=result,
            parameters=parameters
        )

    @classmethod
    def failed(cls, tool_name: str, error: str, parameters: Optional[Any] = None) -> "ToolResult":
        """创建失败结果"""
        return cls(
            tool_name=tool_name,
            status=ExecutionStatus.FAILED,
            error=error,
            parameters=parameters
        )

    @classmethod
    def timeout(cls, tool_name: str, parameters: Optional[Any] = None) -> "ToolResult":
        """创建超时结果"""
        return cls(
            tool_name=tool_name,
            status=ExecutionStatus.TIMEOUT,
            parameters=parameters
        )

    @classmethod
    def cancelled(cls, tool_name: str, parameters: Optional[Any] = None) -> "ToolResult":
        """创建取消结果"""
        return cls(
            tool_name=tool_name,
            status=ExecutionStatus.CANCELLED,
            parameters=parameters
        )

    @classmethod
    def skipped(cls, tool_name: str, parameters: Optional[Any] = None) -> "ToolResult":
        """创建跳过结果"""
        return cls(
            tool_name=tool_name,
            status=ExecutionStatus.SKIPPED,
            parameters=parameters
        )

    def is_success(self) -> bool:
        """检查是否执行成功"""
        return self.status == ExecutionStatus.SUCCESS

    def is_failed(self) -> bool:
        """检查是否执行失败"""
        return self.status == ExecutionStatus.FAILED

    def is_timeout(self) -> bool:
        """检查是否执行超时"""
        return self.status == ExecutionStatus.TIMEOUT

    def is_cancelled(self) -> bool:
        """检查是否被取消"""
        return self.status == ExecutionStatus.CANCELLED

    def is_skipped(self) -> bool:
        """检查是否被跳过"""
        return self.status == ExecutionStatus.SKIPPED

    def get_result_or_throw(self, result_type: Type[T]) -> T:
        """获取结果或抛出异常"""
        if not self.is_success():
            raise RuntimeError(f"Tool execution failed: {self.error}")

        if self.result is None:
            raise RuntimeError("Tool execution result is null")

        if not isinstance(self.result, result_type):
            raise TypeError(f"Result is not of type {result_type.__name__}")

        return self.result

    def get_result_or_default(self, result_type: Type[T], default_value: T) -> T:
        """获取结果或返回默认值"""
        try:
            return self.get_result_or_throw(result_type)
        except Exception:
            return default_value

    def get_error_or_default(self, default_value: str) -> str:
        """获取错误信息或返回默认值"""
        return self.error if self.error is not None else default_value

    def get_execution_time_or_default(self, default_value: int) -> int:
        """获取执行时间或返回默认值"""
        return self.execution_time if self.execution_time is not None else default_value

    def __str__(self) -> str:
        """转换为字符串表示"""
        parts = [f"ToolResult{{tool_name='{self.tool_name}', status={self.status}"]
        
        if self.is_success():
            parts.append(f", result={self.result}")
        else:
            parts.append(f", error='{self.error}'")

        if self.execution_time is not None:
            parts.append(f", execution_time={self.execution_time}ms")

        parts.append("}")
        return "".join(parts)