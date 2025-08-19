"""
文件信息DTO
"""
from typing import Optional
from pydantic import BaseModel, Field


class FileInformation(BaseModel):
    """文件信息"""
    file_name: Optional[str] = Field(None, description="文件名")
    file_desc: Optional[str] = Field(None, description="文件描述")
    oss_url: Optional[str] = Field(None, description="OSS URL")
    domain_url: Optional[str] = Field(None, description="域名URL")
    file_size: Optional[int] = Field(None, description="文件大小")
    file_type: Optional[str] = Field(None, description="文件类型")
    origin_file_name: Optional[str] = Field(None, description="原始文件名")
    origin_file_url: Optional[str] = Field(None, description="原始文件URL")
    origin_oss_url: Optional[str] = Field(None, description="原始OSS URL")
    origin_domain_url: Optional[str] = Field(None, description="原始域名URL")