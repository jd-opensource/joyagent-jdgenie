"""
文件响应DTO
"""
from typing import Optional
from pydantic import BaseModel, Field


class FileResponse(BaseModel):
    """文件响应"""
    request_id: Optional[str] = Field(None, description="请求ID")
    oss_url: Optional[str] = Field(None, description="OSS URL")
    domain_url: Optional[str] = Field(None, description="域名URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小")