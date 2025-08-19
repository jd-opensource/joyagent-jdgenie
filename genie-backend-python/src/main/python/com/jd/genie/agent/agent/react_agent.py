"""
ReAct Agent - Abstract ReAct pattern agent
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import logging
import json
import re
import asyncio

from com.jd.genie.agent.agent.base_agent import BaseAgent
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.tool.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ReActAgent(BaseAgent, ABC):
    """
    ReAct代理 - 基于ReAct模式的智能代理
    """

    @abstractmethod
    def think(self) -> bool:
        """
        思考过程
        """
        pass

    @abstractmethod
    def act(self) -> str:
        """
        执行行动
        """
        pass

    def step(self) -> str:
        """
        执行单个步骤
        """
        should_act = self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return self.act()

    def generate_digital_employee(self, task: str) -> None:
        """
        生成数字员工
        """
        # 1、参数检查
        if not task:
            return

        try:
            # 2. 构建系统消息（提取为独立方法）
            formatted_prompt = self._format_system_prompt(task)
            user_message = Message.user_message(formatted_prompt, None)

            # 3. 调用LLM并处理结果
            summary_future = self.llm.ask(
                self.context,
                [user_message],
                [],
                False,
                0.01
            )

            # 4. 解析响应
            llm_response = asyncio.run(summary_future) if asyncio.iscoroutine(summary_future) else summary_future
            logger.info(f"requestId: {self.context.get_request_id()} task:{task} generateDigitalEmployee: {llm_response}")
            
            json_object = self._parse_digital_employee(llm_response)
            if json_object is not None:
                logger.info(f"requestId:{self.context.get_request_id()} generateDigitalEmployee: {json_object}")
                self.context.get_tool_collection().update_digital_employee(json_object)
                self.context.get_tool_collection().set_current_task(task)
                # 更新 availableTools 添加数字员工
                self.available_tools = self.context.get_tool_collection()
            else:
                logger.error(f"requestId: {self.context.get_request_id()} generateDigitalEmployee failed")

        except Exception as e:
            logger.error(f"requestId: {self.context.get_request_id()} in generateDigitalEmployee failed", exc_info=e)

    def _parse_digital_employee(self, response: str) -> Optional[Dict[str, Any]]:
        """
        解析数字员工大模型响应
        
        格式一：
             ```json
             {
                 "file_tool": "市场洞察专员"
             }
             ```
        格式二：
             {
                 "file_tool": "市场洞察专员"
             }
        """
        if not response or not response.strip():
            return None

        json_string = response
        regex = r"```\s*json([\d\D]+?)```"
        pattern = re.compile(regex)
        matcher = pattern.search(response)
        
        if matcher:
            temp = matcher.group(1).strip()
            if temp:
                json_string = temp

        try:
            return json.loads(json_string)
        except Exception as e:
            logger.error(f"requestId: {self.context.get_request_id()} in parseDigitalEmployee error:", exc_info=e)
            return None

    def _format_system_prompt(self, task: str) -> str:
        """
        提取系统提示格式化逻辑
        """
        digital_employee_prompt = self.get_digital_employee_prompt()
        if digital_employee_prompt is None:
            raise ValueError("System prompt is not configured")

        tool_prompt = ""
        for tool in self.context.get_tool_collection().get_tool_map().values():
            tool_prompt += f"工具名：{tool.get_name()} 工具描述：{tool.get_description()}\n"

        # 替换占位符
        return (digital_employee_prompt
                .replace("{{task}}", task)
                .replace("{{ToolsDesc}}", tool_prompt)
                .replace("{{query}}", self.context.get_query() or ""))