"""
文件DTO
"""
from typing import Optional
from pydantic import BaseModel, Field


class File(BaseModel):
    """文件DTO"""
    oss_url: Optional[str] = Field(None, description="OSS URL")
    domain_url: Optional[str] = Field(None, description="域名URL")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小")
    description: Optional[str] = Field(None, description="文件描述")
    origin_file_name: Optional[str] = Field(None, description="原始文件名")
    origin_oss_url: Optional[str] = Field(None, description="原始OSS URL")
    origin_domain_url: Optional[str] = Field(None, description="原始域名URL")
    is_internal_file: Optional[bool] = Field(None, description="是否为内部文件")