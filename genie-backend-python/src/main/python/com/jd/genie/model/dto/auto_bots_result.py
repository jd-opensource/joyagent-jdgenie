"""
AutoBots结果DTO
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AutoBotsResult(BaseModel):
    """AutoBots结果"""
    status: Optional[str] = Field(None, description="状态")
    response: str = Field(default="", description="增量内容回复")
    response_all: str = Field(default="", description="全量内容回复")
    finished: bool = Field(default=False, description="是否结束")
    use_times: int = Field(default=0, description="使用时间")
    use_tokens: int = Field(default=0, description="使用token数")
    result_map: Optional[Dict[str, Any]] = Field(None, description="结构化输出结果")
    response_type: str = Field(default="markdown", description="大模型响应内容类型")
    trace_id: Optional[str] = Field(None, description="会话ID")
    req_id: Optional[str] = Field(None, description="请求ID")