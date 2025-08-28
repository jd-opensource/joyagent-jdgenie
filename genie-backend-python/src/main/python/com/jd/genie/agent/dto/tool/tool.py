"""
工具类
"""
from typing import Any, Optional
from pydantic import BaseModel, Field


class Tool(BaseModel):
    """工具类"""
    name: Optional[str] = Field(None, description="工具名称")
    description: Optional[str] = Field(None, description="工具描述")
    parameters: Optional[Any] = Field(None, description="工具参数")