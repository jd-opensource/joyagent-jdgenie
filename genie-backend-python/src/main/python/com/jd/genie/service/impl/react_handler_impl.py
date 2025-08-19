"""
React handler implementation.
"""

import logging
from typing import Any, Dict

from ..agent_handler_service import AgentHandlerService
from ...agent.agent.agent_context import AgentContext
from ...agent.agent.react_agent import ReActAgent
from ...agent.agent.react_impl_agent import ReactImplAgent
from ...agent.agent.summary_agent import SummaryAgent
from ...agent.dto.file import File
from ...agent.dto.task_summary_result import TaskSummaryResult
from ...agent.enums.agent_type import AgentType
from ...config.genie_config import GenieConfig
from ...model.req.agent_request import AgentRequest

logger = logging.getLogger(__name__)


class ReactHandlerImpl(AgentHandlerService):
    """Implementation of React handler service."""
    
    def __init__(self, genie_config: GenieConfig):
        """
        Initialize with Genie configuration.
        
        Args:
            genie_config: Genie configuration instance
        """
        self.genie_config = genie_config
    
    async def handle(self, agent_context: AgentContext, request: AgentRequest) -> str:
        """
        Handle React agent processing.
        
        Args:
            agent_context: Agent context
            request: Agent request
            
        Returns:
            Processing result
        """
        executor: ReActAgent = ReactImplAgent(agent_context)
        summary = SummaryAgent(agent_context)
        summary.system_prompt = summary.system_prompt.replace("{{query}}", request.query)
        
        await executor.run(request.query)
        result: TaskSummaryResult = await summary.summary_task_result(
            executor.memory.messages, request.query
        )
        
        task_result: Dict[str, Any] = {
            "taskSummary": result.task_summary
        }
        
        if not result.files:
            if agent_context.product_files:
                file_responses = agent_context.product_files[:]
                # Filter out intermediate search result files
                file_responses = [
                    f for f in file_responses 
                    if f is not None and not f.is_internal_file
                ]
                file_responses.reverse()
                task_result["fileList"] = file_responses
        else:
            task_result["fileList"] = result.files
        
        await agent_context.printer.send("result", task_result)
        
        return ""
    
    def support(self, agent_context: AgentContext, request: AgentRequest) -> bool:
        """
        Check if this handler supports the given request.
        
        Args:
            agent_context: Agent context
            request: Agent request
            
        Returns:
            True if supports React agent type
        """
        return AgentType.REACT.value == request.agent_type