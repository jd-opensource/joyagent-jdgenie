"""
Chat utility functions for request processing.
Chat工具类，用于请求处理
"""
from typing import Optional

from ..agent.enums.auto_bots_result_status import AutoBotsResultStatus
from ..model.dto.auto_bots_result import AutoBotsResult
from ..model.req.agent_request import AgentRequest
from ..model.req.gpt_query_req import GptQueryReq
from .chinese_character_counter import ChineseCharacterCounter


class ChateiUtils:
    """Utility class for chat-related operations."""
    
    SOURCE_MOBILE = "mobile"
    SOURCE_PC = "pc"
    _NO_ANSWER = "哎呀，超出我的知识领域了，换个问题试试吧"
    
    @staticmethod
    def get_request_id_from_gpt_query(request: GptQueryReq) -> str:
        """Get request ID from GPT query request."""
        return ChateiUtils.get_request_id(request.user, request.session_id, request.request_id)
    
    @staticmethod
    def get_request_id(erp: Optional[str], trace_id: str, req_id: str) -> str:
        """
        Generate request ID from ERP, trace ID, and request ID.
        从ERP、跟踪ID和请求ID生成请求ID
        """
        erp = erp.lower() if erp else erp
        
        if ChineseCharacterCounter.has_chinese_characters(erp):
            return f"{trace_id}:{req_id}"
        else:
            return f"{erp}{trace_id}:{req_id}"
    
    @staticmethod
    def to_auto_bots_result(request: AgentRequest, status: str) -> AutoBotsResult:
        """
        Convert agent request to AutoBotsResult.
        将代理请求转换为AutoBotsResult
        """
        result = AutoBotsResult()
        result.trace_id = request.request_id
        result.req_id = request.request_id
        result.status = status
        
        if status == AutoBotsResultStatus.NO.name:
            result.finished = True
            result.response = ChateiUtils._NO_ANSWER
            result.response_all = ChateiUtils._NO_ANSWER
        
        return result