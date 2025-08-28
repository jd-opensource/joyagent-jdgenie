"""
事件消息DTO
"""
from typing import Any, Optional
from pydantic import BaseModel, Field


class EventMessage(BaseModel):
    """事件消息"""
    task_id: Optional[str] = Field(None, description="任务ID")
    task_order: Optional[int] = Field(None, description="任务顺序")
    message_id: Optional[str] = Field(None, description="消息ID")
    message_type: Optional[str] = Field(None, description="消息类型: task、tool、html、file等")
    message_order: Optional[int] = Field(None, description="消息顺序")
    result_map: Optional[Any] = Field(None, description="结果映射")