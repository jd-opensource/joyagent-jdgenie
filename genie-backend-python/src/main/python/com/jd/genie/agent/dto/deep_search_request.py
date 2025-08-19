"""
深度搜索请求DTO
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DeepSearchRequest(BaseModel):
    """深度搜索请求"""
    request_id: Optional[str] = Field(None, description="请求ID")
    query: Optional[str] = Field(None, description="查询内容")
    erp: Optional[str] = Field(None, description="ERP")
    agent_id: Optional[str] = Field(None, description="代理ID")
    optional_configs: Optional[Dict[str, Any]] = Field(None, description="可选配置")
    src_configs: Optional[Dict[str, Any]] = Field(None, description="源配置")
    scene_type: Optional[str] = Field(None, description="场景类型")
    stream: Optional[bool] = Field(None, description="是否流式")
    content_stream: Optional[bool] = Field(None, description="是否内容流式")