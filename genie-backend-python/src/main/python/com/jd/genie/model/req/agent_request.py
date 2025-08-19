"""
Assistant请求DTO
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from ..dto.file_information import FileInformation


class Message(BaseModel):
    """消息"""
    role: Optional[str] = Field(None, description="角色")
    content: Optional[str] = Field(None, description="内容")
    command_code: Optional[str] = Field(None, description="命令代码")
    upload_file: Optional[List[FileInformation]] = Field(None, description="上传文件列表")
    files: Optional[List[FileInformation]] = Field(None, description="文件列表")


class AgentRequest(BaseModel):
    """Assistant请求"""
    request_id: Optional[str] = Field(None, description="请求ID")
    erp: Optional[str] = Field(None, description="ERP")
    query: Optional[str] = Field(None, description="查询内容")
    agent_type: Optional[int] = Field(None, description="代理类型")
    base_prompt: Optional[str] = Field(None, description="基础提示")
    sop_prompt: Optional[str] = Field(None, description="SOP提示")
    is_stream: Optional[bool] = Field(None, description="是否流式")
    messages: Optional[List[Message]] = Field(None, description="消息列表")
    output_style: Optional[str] = Field(None, description="交付物产出格式：html(网页模式）， docs(文档模式）， table(表格模式）")