"""
GPT查询请求DTO
"""
from typing import Optional
from pydantic import BaseModel, Field


class GptQueryReq(BaseModel):
    """GPT查询请求"""
    query: Optional[str] = Field(None, description="查询内容")
    session_id: Optional[str] = Field(None, description="会话ID")
    request_id: Optional[str] = Field(None, description="请求ID")
    deep_think: Optional[int] = Field(None, description="深度思考")
    output_style: Optional[str] = Field(None, description="前端传入交付物格式：html(网页模式），docs(文档模式）， table(表格模式）")
    trace_id: Optional[str] = Field(None, description="跟踪ID")
    user: Optional[str] = Field(None, description="用户")