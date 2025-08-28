"""
代码解释器请求DTO
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """文件信息"""
    file_name: Optional[str] = Field(None, description="文件名")
    origin_file_name: Optional[str] = Field(None, description="原始文件名")
    origin_oss_url: Optional[str] = Field(None, description="原始OSS URL")


class CodeInterpreterRequest(BaseModel):
    """代码解释器请求"""
    request_id: Optional[str] = Field(None, description="请求ID")
    query: Optional[str] = Field(None, description="查询内容")
    task: Optional[str] = Field(None, description="任务")
    file_names: Optional[List[str]] = Field(None, description="文件名列表")
    origin_file_names: Optional[List[FileInfo]] = Field(None, description="原始文件名列表")
    file_name: Optional[str] = Field(None, description="文件名")
    file_description: Optional[str] = Field(None, description="文件描述")
    file_type: Optional[str] = Field(None, description="文件类型")
    stream: Optional[bool] = Field(None, description="是否流式")
    content_stream: Optional[bool] = Field(None, description="是否内容流式")
    stream_mode: Optional[Dict[str, Any]] = Field(None, description="流式模式")