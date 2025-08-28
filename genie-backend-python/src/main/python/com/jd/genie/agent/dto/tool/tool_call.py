"""
工具调用类
"""
from typing import Optional
from pydantic import BaseModel, Field


class Function(BaseModel):
    """函数信息类"""
    name: Optional[str] = Field(None, description="函数名称")
    arguments: Optional[str] = Field(None, description="函数参数")


class ToolCall(BaseModel):
    """工具调用类"""
    id: Optional[str] = Field(None, description="调用ID")
    type: Optional[str] = Field(None, description="调用类型")
    function: Optional[Function] = Field(None, description="函数信息")