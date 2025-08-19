"""
React Implementation Agent - Tool execution agent with React pattern
"""
from typing import List, Optional, Dict, Any
import logging
import json
import asyncio

from com.jd.genie.agent.agent.react_agent import ReActAgent
from com.jd.genie.agent.agent.agent_context import AgentContext
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.dto.tool.tool_call import ToolCall
from com.jd.genie.agent.dto.tool.tool_choice import ToolChoice
from com.jd.genie.agent.enums.agent_state import AgentState
from com.jd.genie.agent.enums.role_type import RoleType
from com.jd.genie.agent.llm.llm import LLM
from com.jd.genie.agent.prompt.tool_call_prompt import ToolCallPrompt
from com.jd.genie.agent.tool.base_tool import BaseTool
from com.jd.genie.agent.util.file_util import FileUtil
from com.jd.genie.agent.util.spring_context_holder import SpringContextHolder
from com.jd.genie.config.genie_config import GenieConfig
from com.jd.genie.model.response.agent_response import AgentResponse

logger = logging.getLogger(__name__)


class ReactImplAgent(ReActAgent):
    """
    工具调用代理 - 处理工具/函数调用的基础代理类
    """

    def __init__(self, context: AgentContext):
        super().__init__()
        self.tool_calls: List[ToolCall] = []
        self.max_observe: Optional[int] = None
        self.system_prompt_snapshot: Optional[str] = None
        self.next_step_prompt_snapshot: Optional[str] = None

        self.set_name("react")
        self.set_description("an agent that can execute tool calls.")
        
        application_context = SpringContextHolder.get_application_context()
        genie_config = application_context.get_bean(GenieConfig)

        tool_prompt = ""
        for tool in context.get_tool_collection().get_tool_map().values():
            tool_prompt += f"工具名：{tool.get_name()} 工具描述：{tool.get_description()}\n"

        prompt_key = "default"
        next_prompt_key = "default"

        system_prompt = (genie_config.get_react_system_prompt_map().get(prompt_key, ToolCallPrompt.SYSTEM_PROMPT)
                        .replace("{{tools}}", tool_prompt)
                        .replace("{{query}}", context.get_query() or "")
                        .replace("{{date}}", context.get_date_info() or "")
                        .replace("{{basePrompt}}", context.get_base_prompt() or ""))
        
        next_step_prompt = (genie_config.get_react_next_step_prompt_map().get(next_prompt_key, ToolCallPrompt.NEXT_STEP_PROMPT)
                           .replace("{{tools}}", tool_prompt)
                           .replace("{{query}}", context.get_query() or "")
                           .replace("{{date}}", context.get_date_info() or "")
                           .replace("{{basePrompt}}", context.get_base_prompt() or ""))

        self.set_system_prompt(system_prompt)
        self.set_next_step_prompt(next_step_prompt)
        
        self.system_prompt_snapshot = self.get_system_prompt()
        self.next_step_prompt_snapshot = self.get_next_step_prompt()

        self.set_printer(context.printer)
        self.set_max_steps(genie_config.get_react_max_steps())
        self.set_llm(LLM(genie_config.get_react_model_name(), ""))
        self.set_context(context)

        # 初始化工具集合
        self.available_tools = context.get_tool_collection()
        self.set_digital_employee_prompt(genie_config.get_digital_employee_prompt())

    def think(self) -> bool:
        """
        思考过程
        """
        # 获取文件内容
        files_str = FileUtil.format_file_info(self.context.get_product_files(), True)
        self.set_system_prompt(self.system_prompt_snapshot.replace("{{files}}", files_str))
        self.set_next_step_prompt(self.next_step_prompt_snapshot.replace("{{files}}", files_str))

        if self.get_memory().get_last_message().role != RoleType.USER:
            user_msg = Message.user_message(self.get_next_step_prompt(), None)
            self.get_memory().add_message(user_msg)

        try:
            # 获取带工具选项的响应
            self.context.set_stream_message_type("tool_thought")

            future = self.get_llm().ask_tool(
                self.context,
                self.get_memory().get_messages(),
                Message.system_message(self.get_system_prompt(), None),
                self.available_tools,
                ToolChoice.AUTO,
                None,
                self.context.get_is_stream(),
                300
            )

            response = asyncio.run(future) if asyncio.iscoroutine(future) else future
            self.tool_calls = response.get_tool_calls() if response.get_tool_calls() else []

            # 记录响应信息
            if not self.context.get_is_stream() and response.get_content() and response.get_content():
                self.printer.send("tool_thought", response.get_content())

            # 创建并添加助手消息
            assistant_msg = (Message.from_tool_calls(response.get_content(), response.get_tool_calls())
                           if response.get_tool_calls() and self.llm.get_function_call_type() != "struct_parse"
                           else Message.assistant_message(response.get_content(), None))
            self.get_memory().add_message(assistant_msg)

        except Exception as e:
            logger.error(f"{self.context.get_request_id()} react think error", exc_info=e)
            self.get_memory().add_message(Message.assistant_message(
                f"Error encountered while processing: {e}", None))
            self.set_state(AgentState.FINISHED)
            return False

        return True

    def act(self) -> str:
        """
        执行行动
        """
        if not self.tool_calls:
            self.set_state(AgentState.FINISHED)
            return self.get_memory().get_last_message().content

        # action
        tool_results = self.execute_tools(self.tool_calls)
        results = []
        
        for command in self.tool_calls:
            result = tool_results.get(command.id)
            if command.function.name not in ["code_interpreter", "report_tool", "file_tool", "deep_search"]:
                tool_name = command.function.name
                tool_result = AgentResponse.ToolResult.builder() \
                    .tool_name(tool_name) \
                    .tool_param(json.loads(command.function.arguments)) \
                    .tool_result(result) \
                    .build()
                self.printer.send("tool_result", tool_result, None)

            if self.max_observe is not None:
                result = result[:min(len(result), self.max_observe)]

            # 添加工具响应到记忆
            if self.llm.get_function_call_type() == "struct_parse":
                content = self.get_memory().get_last_message().content
                self.get_memory().get_last_message().content = content + "\n 工具执行结果为:\n" + result
            else:  # function_call
                tool_msg = Message.tool_message(result, command.id, None)
                self.get_memory().add_message(tool_msg)
            
            results.append(result)

        return "\n\n".join(results)

    def run(self, request: str) -> str:
        """
        运行代理
        """
        return super().run(request)

    # Getter and Setter methods
    def get_tool_calls(self) -> List[ToolCall]:
        return self.tool_calls

    def set_tool_calls(self, tool_calls: List[ToolCall]) -> 'ReactImplAgent':
        self.tool_calls = tool_calls if tool_calls else []
        return self

    def get_max_observe(self) -> Optional[int]:
        return self.max_observe

    def set_max_observe(self, max_observe: int) -> 'ReactImplAgent':
        self.max_observe = max_observe
        return self

    def get_system_prompt_snapshot(self) -> Optional[str]:
        return self.system_prompt_snapshot

    def set_system_prompt_snapshot(self, system_prompt_snapshot: str) -> 'ReactImplAgent':
        self.system_prompt_snapshot = system_prompt_snapshot
        return self

    def get_next_step_prompt_snapshot(self) -> Optional[str]:
        return self.next_step_prompt_snapshot

    def set_next_step_prompt_snapshot(self, next_step_prompt_snapshot: str) -> 'ReactImplAgent':
        self.next_step_prompt_snapshot = next_step_prompt_snapshot
        return self