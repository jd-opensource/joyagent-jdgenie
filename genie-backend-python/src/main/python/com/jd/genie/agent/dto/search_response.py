"""
搜索响应DTO
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchDoc(BaseModel):
    """搜索文档"""
    source_url: Optional[str] = Field(None, description="源URL")
    page_content: Optional[str] = Field(None, description="页面内容")
    name: Optional[str] = Field(None, description="名称")


class SearchResponse(BaseModel):
    """搜索响应"""
    code: Optional[int] = Field(None, description="响应码")
    data: Optional[List[SearchDoc]] = Field(None, description="搜索文档列表")