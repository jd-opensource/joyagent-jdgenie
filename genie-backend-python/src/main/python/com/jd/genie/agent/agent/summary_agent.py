"""
Summary Agent - Agent for summarizing task results
"""
from typing import List, Optional, Dict, Any
import logging
import asyncio
import time

from com.jd.genie.agent.agent.base_agent import BaseAgent
from com.jd.genie.agent.agent.agent_context import AgentContext
from com.jd.genie.agent.dto.file import File
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.dto.task_summary_result import TaskSummaryResult
from com.jd.genie.agent.llm.llm import LLM
from com.jd.genie.agent.util.spring_context_holder import SpringContextHolder
from com.jd.genie.config.genie_config import GenieConfig

logger = logging.getLogger(__name__)


class SummaryAgent(BaseAgent):
    """
    总结代理 - 用于总结任务执行结果的代理
    """

    LOG_FLAG = "summaryTaskResult"

    def __init__(self, context: AgentContext):
        super().__init__()
        self.request_id: Optional[str] = None
        self.message_size_limit: int = 0

        application_context = SpringContextHolder.get_application_context()
        genie_config = application_context.get_bean(GenieConfig)
        
        self.set_system_prompt(genie_config.get_summary_system_prompt())
        self.set_context(context)
        self.set_request_id(context.get_request_id())
        
        model_name = (genie_config.get_planner_model_name() 
                     if context.get_agent_type() == 3 
                     else genie_config.get_react_model_name())
        self.set_llm(LLM(model_name, ""))
        self.set_message_size_limit(genie_config.get_message_size_limit())

    def step(self) -> str:
        """
        执行单个步骤
        """
        return ""

    def _create_file_info(self) -> str:
        """
        构造文件信息
        """
        files = self.context.get_product_files()
        if not files:
            logger.info(f"requestId: {self.request_id} no files found in context")
            return ""
        
        logger.info(f"requestId: {self.request_id} {self.LOG_FLAG} product files:{files}")
        
        result = "\n".join([
            f"{file.get_file_name()} : {file.get_description()}"
            for file in files
            if not file.get_is_internal_file()  # 过滤内部文件
        ])

        logger.info(f"requestId: {self.request_id} generated file info: {result}")
        return result

    def _format_system_prompt(self, task_history: str, query: str) -> str:
        """
        提取系统提示格式化逻辑
        """
        system_prompt = self.get_system_prompt()
        if system_prompt is None:
            logger.error(f"requestId: {self.request_id} {self.LOG_FLAG} systemPrompt is null")
            raise ValueError("System prompt is not configured")

        # 替换占位符
        return (system_prompt
                .replace("{{taskHistory}}", task_history)
                .replace("{{fileNameDesc}}", self._create_file_info())
                .replace("{{query}}", query))

    def _create_system_message(self, content: str) -> Message:
        """
        提取消息创建逻辑
        """
        return Message.user_message(content, None)  # 如果需要更复杂的消息构建，可扩展

    def _parse_llm_response(self, llm_response: str) -> TaskSummaryResult:
        """
        解析LLM响应并处理文件关联
        """
        if not llm_response:
            logger.error(f"requestId: {self.request_id} pattern matcher failed for response is null")

        parts1 = llm_response.split("$$$")
        if len(parts1) < 2:
            return TaskSummaryResult.builder().task_summary(parts1[0]).build()

        summary = parts1[0]
        file_names = parts1[1]

        files = self.context.get_product_files()
        if not files:
            logger.error(f"requestId: {self.request_id} llmResponse:{llm_response} productFile list is empty")
            # 文件列表为空，交付物中不显示文件
            return TaskSummaryResult.builder().task_summary(summary).build()
        
        # 反转文件列表
        files.reverse()
        
        product = []
        items = file_names.split("、")
        
        for item in items:
            trimmed_item = item.strip()
            if not trimmed_item:
                continue
                
            for file in files:
                if trimmed_item in file.get_file_name().strip():
                    logger.info(f"requestId: {self.request_id} add file:{file}")
                    product.append(file)
                    break

        return TaskSummaryResult.builder().task_summary(summary).files(product).build()

    def summary_task_result(self, messages: List[Message], query: str) -> TaskSummaryResult:
        """
        总结任务
        """
        start_time = int(time.time() * 1000)  # Current time in milliseconds
        
        # 1. 参数校验（可选）
        if not messages or not query:
            logger.warning(f"requestId: {self.request_id} summaryTaskResult messages:{messages} or query:{query} is empty")
            return TaskSummaryResult.builder().task_summary("").build()

        try:
            # 2. 构建系统消息（提取为独立方法）
            logger.info(f"requestId: {self.request_id} summaryTaskResult: messages:{len(messages)}")
            
            sb = []
            for message in messages:
                content = message.get_content()
                if content and len(content) > self.get_message_size_limit():
                    logger.info(f"requestId: {self.request_id} message truncate,{message}")
                    content = content[:self.get_message_size_limit()]
                sb.append(f"role:{message.get_role()} content:{content}\n")
            
            formatted_prompt = self._format_system_prompt("".join(sb), query)
            user_message = self._create_system_message(formatted_prompt)

            # 3. 调用LLM并处理结果
            summary_future = self.get_llm().ask(
                self.context,
                [user_message],
                [],
                False,
                0.01
            )

            # 5. 解析响应
            llm_response = asyncio.run(summary_future) if asyncio.iscoroutine(summary_future) else summary_future
            logger.info(f"requestId: {self.request_id} summaryTaskResult: {llm_response}")

            return self._parse_llm_response(llm_response)
            
        except Exception as e:
            logger.error(f"requestId: {self.request_id} in summaryTaskResult failed", exc_info=e)
            return TaskSummaryResult.builder().task_summary("任务执行失败，请联系管理员！").build()

    # Getter and Setter methods
    def get_request_id(self) -> Optional[str]:
        return self.request_id

    def set_request_id(self, request_id: str) -> 'SummaryAgent':
        self.request_id = request_id
        return self

    def get_message_size_limit(self) -> int:
        return self.message_size_limit

    def set_message_size_limit(self, message_size_limit: int) -> 'SummaryAgent':
        self.message_size_limit = message_size_limit
        return self