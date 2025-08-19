"""
代码解释器响应DTO
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    """文件信息"""
    file_name: Optional[str] = Field(None, description="文件名")
    oss_url: Optional[str] = Field(None, description="OSS URL")
    domain_url: Optional[str] = Field(None, description="域名URL")
    file_size: Optional[int] = Field(None, description="文件大小")


class CodeInterpreterResponse(BaseModel):
    """代码解释器响应"""
    requests_id: Optional[str] = Field(None, description="请求ID")
    result_type: Optional[str] = Field(None, description="结果类型")
    content: Optional[str] = Field(None, description="内容")
    code: Optional[str] = Field(None, description="代码")
    code_output: Optional[str] = Field(None, description="代码输出")
    file_info: Optional[List[FileInfo]] = Field(None, description="文件信息列表")
    explain: Optional[str] = Field(None, description="解释")
    step: Optional[int] = Field(None, description="步骤")
    data: Optional[str] = Field(None, description="数据")
    is_final: Optional[bool] = Field(None, description="是否最终结果")