"""
文件请求DTO
"""
from typing import Optional
from pydantic import BaseModel, Field


class FileRequest(BaseModel):
    """文件请求"""
    request_id: Optional[str] = Field(None, description="请求ID")
    file_name: Optional[str] = Field(None, description="文件名")
    description: Optional[str] = Field(None, description="描述")
    content: Optional[str] = Field(None, description="内容")