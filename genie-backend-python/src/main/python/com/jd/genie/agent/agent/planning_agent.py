"""
Planning Agent - Creates and manages task plans
"""
from typing import List, Optional, Dict, Any
import logging
import asyncio
import time

from com.jd.genie.agent.agent.react_agent import ReActAgent
from com.jd.genie.agent.agent.agent_context import AgentContext
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.dto.tool.tool_call import ToolCall
from com.jd.genie.agent.dto.tool.tool_choice import ToolChoice
from com.jd.genie.agent.enums.agent_state import AgentState
from com.jd.genie.agent.enums.role_type import RoleType
from com.jd.genie.agent.llm.llm import LLM
from com.jd.genie.agent.prompt.planning_prompt import PlanningPrompt
from com.jd.genie.agent.tool.base_tool import BaseTool
from com.jd.genie.agent.tool.common.planning_tool import PlanningTool
from com.jd.genie.agent.util.file_util import FileUtil
from com.jd.genie.agent.util.spring_context_holder import SpringContextHolder
from com.jd.genie.config.genie_config import GenieConfig

logger = logging.getLogger(__name__)


class PlanningAgent(ReActAgent):
    """
    规划代理 - 创建和管理任务计划的代理
    """

    def __init__(self, context: AgentContext):
        super().__init__()
        self.tool_calls: List[ToolCall] = []
        self.max_observe: Optional[int] = None
        self.planning_tool: PlanningTool = PlanningTool()
        self.is_close_update: bool = False
        self.system_prompt_snapshot: Optional[str] = None
        self.next_step_prompt_snapshot: Optional[str] = None
        self.plan_id: Optional[str] = None

        self.set_name("planning")
        self.set_description("An agent that creates and manages plans to solve tasks")
        
        application_context = SpringContextHolder.get_application_context()
        genie_config = application_context.get_bean(GenieConfig)

        tool_prompt = ""
        for tool in context.get_tool_collection().get_tool_map().values():
            tool_prompt += f"工具名：{tool.get_name()} 工具描述：{tool.get_description()}\n"

        prompt_key = "default"
        next_prompt_key = "default"

        system_prompt = (genie_config.get_planner_system_prompt_map().get(prompt_key, PlanningPrompt.SYSTEM_PROMPT)
                        .replace("{{tools}}", tool_prompt)
                        .replace("{{query}}", context.get_query() or "")
                        .replace("{{date}}", context.get_date_info() or "")
                        .replace("{{sopPrompt}}", context.get_sop_prompt() or ""))
        
        next_step_prompt = (genie_config.get_planner_next_step_prompt_map().get(next_prompt_key, PlanningPrompt.NEXT_STEP_PROMPT)
                           .replace("{{tools}}", tool_prompt)
                           .replace("{{query}}", context.get_query() or "")
                           .replace("{{date}}", context.get_date_info() or "")
                           .replace("{{sopPrompt}}", context.get_sop_prompt() or ""))

        self.set_system_prompt(system_prompt)
        self.set_next_step_prompt(next_step_prompt)
        
        self.system_prompt_snapshot = self.get_system_prompt()
        self.next_step_prompt_snapshot = self.get_next_step_prompt()

        self.set_printer(context.printer)
        self.set_max_steps(genie_config.get_planner_max_steps())
        self.set_llm(LLM(genie_config.get_planner_model_name(), ""))

        self.set_context(context)
        self.is_close_update = genie_config.get_planning_close_update() == "1"

        # 初始化工具集合
        self.available_tools.add_tool(self.planning_tool)
        self.planning_tool.set_agent_context(context)

    def think(self) -> bool:
        """
        思考过程
        """
        start_time = int(time.time() * 1000)  # Current time in milliseconds
        
        # 获取文件内容
        files_str = FileUtil.format_file_info(self.context.get_product_files(), False)
        self.set_system_prompt(self.system_prompt_snapshot.replace("{{files}}", files_str))
        self.set_next_step_prompt(self.next_step_prompt_snapshot.replace("{{files}}", files_str))
        logger.info(f"{self.context.get_request_id()} planer fileStr {files_str}")

        # 关闭了动态更新Plan，直接执行下一个task
        if self.is_close_update:
            if self.planning_tool.get_plan() is not None:
                self.planning_tool.step_plan()
                return True

        try:
            if self.get_memory().get_last_message().role != RoleType.USER:
                user_msg = Message.user_message(self.get_next_step_prompt(), None)
                self.get_memory().add_message(user_msg)

            self.context.set_stream_message_type("plan_thought")
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
                self.printer.send("plan_thought", response.get_content())

            # 记录响应信息
            logger.info(f"{self.context.get_request_id()} {self.get_name()}'s thoughts: {response.get_content()}")
            logger.info(f"{self.context.get_request_id()} {self.get_name()} selected "
                       f"{len(response.get_tool_calls()) if response.get_tool_calls() else 0} tools to use")

            # 创建并添加助手消息
            assistant_msg = (Message.from_tool_calls(response.get_content(), response.get_tool_calls())
                           if response.get_tool_calls() and self.llm.get_function_call_type() != "struct_parse"
                           else Message.assistant_message(response.get_content(), None))

            self.get_memory().add_message(assistant_msg)

        except Exception as e:
            logger.error(f"{self.context.get_request_id()} think error", exc_info=e)

        return True

    def act(self) -> str:
        """
        执行行动
        """
        # 关闭了动态更新Plan，直接执行下一个task
        if self.is_close_update:
            if self.planning_tool.get_plan() is not None:
                return self._get_next_task()

        results = []
        start_time = int(time.time() * 1000)  # Current time in milliseconds
        
        for tool_call in self.tool_calls:
            result = self.execute_tool(tool_call)
            if self.max_observe is not None:
                result = result[:min(len(result), self.max_observe)]
            results.append(result)

            # 添加工具响应到记忆
            if self.llm.get_function_call_type() == "struct_parse":
                content = self.get_memory().get_last_message().content
                self.get_memory().get_last_message().content = content + "\n 工具执行结果为:\n" + result
            else:  # function_call
                tool_msg = Message.tool_message(result, tool_call.id, None)
                self.get_memory().add_message(tool_msg)

        if self.planning_tool.get_plan() is not None:
            if self.is_close_update:
                self.planning_tool.step_plan()
            return self._get_next_task()

        return "\n\n".join(results)

    def _get_next_task(self) -> str:
        """
        获取下一个任务
        """
        all_complete = True
        for status in self.planning_tool.get_plan().get_step_status():
            if status != "completed":
                all_complete = False
                break

        if all_complete:
            self.set_state(AgentState.FINISHED)
            self.printer.send("plan", self.planning_tool.get_plan())
            return "finish"

        if self.planning_tool.get_plan().get_current_step():
            self.set_state(AgentState.FINISHED)
            current_steps = self.planning_tool.get_plan().get_current_step().split("<sep>")
            self.printer.send("plan", self.planning_tool.get_plan())
            for step in current_steps:
                self.printer.send("task", step)
            return self.planning_tool.get_plan().get_current_step()
        
        return ""

    def run(self, request: str) -> str:
        """
        运行代理
        """
        if self.planning_tool.get_plan() is None:
            genie_config = SpringContextHolder.get_application_context().get_bean(GenieConfig)
            request = genie_config.get_plan_pre_prompt() + request
        return super().run(request)

    # Getter and Setter methods
    def get_tool_calls(self) -> List[ToolCall]:
        return self.tool_calls

    def set_tool_calls(self, tool_calls: List[ToolCall]) -> 'PlanningAgent':
        self.tool_calls = tool_calls if tool_calls else []
        return self

    def get_max_observe(self) -> Optional[int]:
        return self.max_observe

    def set_max_observe(self, max_observe: int) -> 'PlanningAgent':
        self.max_observe = max_observe
        return self

    def get_planning_tool(self) -> PlanningTool:
        return self.planning_tool

    def set_planning_tool(self, planning_tool: PlanningTool) -> 'PlanningAgent':
        self.planning_tool = planning_tool
        return self

    def get_is_close_update(self) -> bool:
        return self.is_close_update

    def set_is_close_update(self, is_close_update: bool) -> 'PlanningAgent':
        self.is_close_update = is_close_update
        return self

    def get_system_prompt_snapshot(self) -> Optional[str]:
        return self.system_prompt_snapshot

    def set_system_prompt_snapshot(self, system_prompt_snapshot: str) -> 'PlanningAgent':
        self.system_prompt_snapshot = system_prompt_snapshot
        return self

    def get_next_step_prompt_snapshot(self) -> Optional[str]:
        return self.next_step_prompt_snapshot

    def set_next_step_prompt_snapshot(self, next_step_prompt_snapshot: str) -> 'PlanningAgent':
        self.next_step_prompt_snapshot = next_step_prompt_snapshot
        return self

    def get_plan_id(self) -> Optional[str]:
        return self.plan_id

    def set_plan_id(self, plan_id: str) -> 'PlanningAgent':
        self.plan_id = plan_id
        return self