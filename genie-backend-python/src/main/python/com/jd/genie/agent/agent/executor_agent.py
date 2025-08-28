"""
Executor Agent - Tool execution agent
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


class ExecutorAgent(ReActAgent):
    """
    工具调用代理 - 处理工具/函数调用的基础代理类
    """

    def __init__(self, context: AgentContext):
        super().__init__()
        self.tool_calls: List[ToolCall] = []
        self.max_observe: Optional[int] = None
        self.system_prompt_snapshot: Optional[str] = None
        self.next_step_prompt_snapshot: Optional[str] = None
        self.task_id: int = 0

        self.set_name("executor")
        self.set_description("an agent that can execute tool calls.")
        
        application_context = SpringContextHolder.get_application_context()
        genie_config = application_context.get_bean(GenieConfig)

        tool_prompt = ""
        for tool in context.get_tool_collection().get_tool_map().values():
            tool_prompt += f"工具名：{tool.get_name()} 工具描述：{tool.get_description()}\n"

        prompt_key = "default"
        sop_prompt_key = "default"
        next_prompt_key = "default"

        system_prompt = (genie_config.get_executor_system_prompt_map().get(prompt_key, ToolCallPrompt.SYSTEM_PROMPT)
                        .replace("{{tools}}", tool_prompt)
                        .replace("{{query}}", context.get_query() or "")
                        .replace("{{date}}", context.get_date_info() or "")
                        .replace("{{sopPrompt}}", context.get_sop_prompt() or "")
                        .replace("{{executorSopPrompt}}", genie_config.get_executor_sop_prompt_map().get(sop_prompt_key, "")))
        
        next_step_prompt = (genie_config.get_executor_next_step_prompt_map().get(next_prompt_key, ToolCallPrompt.NEXT_STEP_PROMPT)
                           .replace("{{tools}}", tool_prompt)
                           .replace("{{query}}", context.get_query() or "")
                           .replace("{{date}}", context.get_date_info() or "")
                           .replace("{{sopPrompt}}", context.get_sop_prompt() or "")
                           .replace("{{executorSopPrompt}}", genie_config.get_executor_sop_prompt_map().get(sop_prompt_key, "")))

        self.set_system_prompt(system_prompt)
        self.set_next_step_prompt(next_step_prompt)
        
        self.system_prompt_snapshot = self.get_system_prompt()
        self.next_step_prompt_snapshot = self.get_next_step_prompt()

        self.set_printer(context.printer)
        self.set_max_steps(genie_config.get_planner_max_steps())
        self.set_llm(LLM(genie_config.get_executor_model_name(), ""))
        
        self.set_context(context)
        self.max_observe = int(genie_config.get_max_observe())

        # 初始化工具集合
        self.available_tools = context.get_tool_collection()
        self.set_digital_employee_prompt(genie_config.get_digital_employee_prompt())

        self.task_id = 0

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
            logger.info(f"{self.context.get_request_id()} executor ask tool {json.dumps(self.available_tools.__dict__)}")
            
            future = self.get_llm().ask_tool(
                self.context,
                self.get_memory().get_messages(),
                Message.system_message(self.get_system_prompt(), None),
                self.available_tools,
                ToolChoice.AUTO,
                None,
                False,
                300
            )

            response = asyncio.run(future) if asyncio.iscoroutine(future) else future
            self.tool_calls = response.get_tool_calls() if response.get_tool_calls() else []

            # 记录响应信息
            if response.get_content() and response.get_content().strip():
                think_result = response.get_content()
                sub_type = "taskThought"
                if not self.tool_calls:
                    task_summary = {
                        "taskSummary": response.get_content(),
                        "fileList": self.context.get_task_product_files()
                    }
                    think_result = json.dumps(task_summary)
                    sub_type = "taskSummary"
                    self.printer.send("task_summary", task_summary)
                else:
                    self.printer.send("tool_thought", response.get_content())

            # 创建并添加助手消息
            assistant_msg = (Message.from_tool_calls(response.get_content(), response.get_tool_calls())
                           if response.get_tool_calls() and self.llm.get_function_call_type() != "struct_parse"
                           else Message.assistant_message(response.get_content(), None))
            self.get_memory().add_message(assistant_msg)

        except Exception as e:
            logger.error(f"Oops! The {self.get_name()}'s thinking process hit a snag: {e}")
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
            genie_config = SpringContextHolder.get_application_context().get_bean(GenieConfig)
            self.set_state(AgentState.FINISHED)
            
            # 删除工具结果
            if genie_config.get_clear_tool_message() == "1":
                self.get_memory().clear_tool_context()
            
            # 返回固定话术
            if genie_config.get_task_complete_desc():
                return genie_config.get_task_complete_desc()
            
            return self.get_memory().get_last_message().content

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
        self.generate_digital_employee(request)
        genie_config = SpringContextHolder.get_application_context().get_bean(GenieConfig)
        request = genie_config.get_task_pre_prompt() + request
        # 更新当前task
        self.context.set_task(request)
        return super().run(request)

    # Getter and Setter methods
    def get_tool_calls(self) -> List[ToolCall]:
        return self.tool_calls

    def set_tool_calls(self, tool_calls: List[ToolCall]) -> 'ExecutorAgent':
        self.tool_calls = tool_calls if tool_calls else []
        return self

    def get_max_observe(self) -> Optional[int]:
        return self.max_observe

    def set_max_observe(self, max_observe: int) -> 'ExecutorAgent':
        self.max_observe = max_observe
        return self

    def get_system_prompt_snapshot(self) -> Optional[str]:
        return self.system_prompt_snapshot

    def set_system_prompt_snapshot(self, system_prompt_snapshot: str) -> 'ExecutorAgent':
        self.system_prompt_snapshot = system_prompt_snapshot
        return self

    def get_next_step_prompt_snapshot(self) -> Optional[str]:
        return self.next_step_prompt_snapshot

    def set_next_step_prompt_snapshot(self, next_step_prompt_snapshot: str) -> 'ExecutorAgent':
        self.next_step_prompt_snapshot = next_step_prompt_snapshot
        return self

    def get_task_id(self) -> int:
        return self.task_id

    def set_task_id(self, task_id: int) -> 'ExecutorAgent':
        self.task_id = task_id
        return self