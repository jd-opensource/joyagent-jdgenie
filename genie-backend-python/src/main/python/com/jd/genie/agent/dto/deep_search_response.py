"""
深度搜索响应DTO
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchDoc(BaseModel):
    """搜索文档"""
    doc_type: Optional[str] = Field(None, description="文档类型")
    content: Optional[str] = Field(None, description="内容")
    title: Optional[str] = Field(None, description="标题")
    link: Optional[str] = Field(None, description="链接")


class SearchResult(BaseModel):
    """搜索结果"""
    query: Optional[List[str]] = Field(None, description="查询列表")
    docs: Optional[List[List[SearchDoc]]] = Field(None, description="文档列表")


class DeepSearchResponse(BaseModel):
    """深度搜索响应"""
    request_id: Optional[str] = Field(None, description="请求ID")
    query: Optional[str] = Field(None, description="查询内容")
    answer: Optional[str] = Field(None, description="答案")
    search_result: Optional[SearchResult] = Field(None, description="搜索结果")
    is_final: Optional[bool] = Field(None, description="是否最终结果")
    search_finish: Optional[bool] = Field(None, description="搜索结果是否结束")
    message_type: Optional[str] = Field(None, description="消息类型: extend、search、report")