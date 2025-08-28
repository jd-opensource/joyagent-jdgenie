"""
Base Agent - Abstract base class for all agents
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from com.jd.genie.agent.agent.agent_context import AgentContext
from com.jd.genie.agent.dto.memory import Memory
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.dto.tool.tool_call import ToolCall
from com.jd.genie.agent.enums.agent_state import AgentState
from com.jd.genie.agent.enums.role_type import RoleType
from com.jd.genie.agent.llm.llm import LLM
from com.jd.genie.agent.printer.printer import Printer
from com.jd.genie.agent.tool.tool_collection import ToolCollection

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    代理基类 - 管理代理状态和执行的基础类
    """

    def __init__(self):
        # 核心属性
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.system_prompt: Optional[str] = None
        self.next_step_prompt: Optional[str] = None
        self.available_tools: ToolCollection = ToolCollection()
        self.memory: Memory = Memory()
        self.llm: Optional[LLM] = None
        self.context: Optional[AgentContext] = None

        # 执行控制
        self.state: AgentState = AgentState.IDLE
        self.max_steps: int = 10
        self.current_step: int = 0
        self.duplicate_threshold: int = 2

        # emitter
        self.printer: Optional[Printer] = None

        # digital employee prompt
        self.digital_employee_prompt: Optional[str] = None

    @abstractmethod
    def step(self) -> str:
        """
        执行单个步骤
        """
        pass

    def run(self, query: str) -> str:
        """
        运行代理主循环
        """
        self.set_state(AgentState.IDLE)

        if query:
            self.update_memory(RoleType.USER, query, None)

        results = []
        try:
            while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
                self.current_step += 1
                logger.info(f"{self.context.get_request_id()} {self.get_name()} "
                           f"Executing step {self.current_step}/{self.max_steps}")
                step_result = self.step()
                results.append(step_result)

            if self.current_step >= self.max_steps:
                self.current_step = 0
                self.state = AgentState.IDLE
                results.append(f"Terminated: Reached max steps ({self.max_steps})")
        except Exception as e:
            self.state = AgentState.ERROR
            raise e

        return results[-1] if results else "No steps executed"

    def update_memory(self, role: RoleType, content: str, base64_image: Optional[str], *args) -> None:
        """
        更新代理记忆
        """
        if role == RoleType.USER:
            message = Message.user_message(content, base64_image)
        elif role == RoleType.SYSTEM:
            message = Message.system_message(content, base64_image)
        elif role == RoleType.ASSISTANT:
            message = Message.assistant_message(content, base64_image)
        elif role == RoleType.TOOL:
            tool_call_id = args[0] if args else None
            message = Message.tool_message(content, tool_call_id, base64_image)
        else:
            raise ValueError(f"Unsupported role type: {role}")

        self.memory.add_message(message)

    def execute_tool(self, command: ToolCall) -> str:
        """
        执行单个工具调用
        """
        if not command or not command.function or not command.function.name:
            return "Error: Invalid function call format"

        name = command.function.name
        try:
            # 解析参数
            args = json.loads(command.function.arguments)

            # 执行工具
            result = self.available_tools.execute(name, args)
            logger.info(f"{self.context.get_request_id()} execute tool: {name} {args} result {result}")
            
            # 格式化结果
            if result is not None:
                return str(result)
        except Exception as e:
            logger.error(f"{self.context.get_request_id()} execute tool {name} failed", exc_info=e)

        return f"Tool {name} Error."

    def execute_tools(self, commands: List[ToolCall]) -> Dict[str, str]:
        """
        并发执行多个工具调用命令并返回执行结果
        
        Args:
            commands: 工具调用命令列表
            
        Returns:
            返回工具执行结果映射，key为工具ID，value为执行结果
        """
        result = {}
        
        def execute_single_tool(tool_call: ToolCall) -> None:
            tool_result = self.execute_tool(tool_call)
            result[tool_call.id] = tool_result

        # 使用ThreadPoolExecutor进行并发执行
        with ThreadPoolExecutor(max_workers=len(commands)) as executor:
            futures = [executor.submit(execute_single_tool, tool_call) for tool_call in commands]
            # 等待所有任务完成
            for future in futures:
                future.result()

        return result

    # Getter and Setter methods
    def get_name(self) -> Optional[str]:
        return self.name

    def set_name(self, name: str) -> 'BaseAgent':
        self.name = name
        return self

    def get_description(self) -> Optional[str]:
        return self.description

    def set_description(self, description: str) -> 'BaseAgent':
        self.description = description
        return self

    def get_system_prompt(self) -> Optional[str]:
        return self.system_prompt

    def set_system_prompt(self, system_prompt: str) -> 'BaseAgent':
        self.system_prompt = system_prompt
        return self

    def get_next_step_prompt(self) -> Optional[str]:
        return self.next_step_prompt

    def set_next_step_prompt(self, next_step_prompt: str) -> 'BaseAgent':
        self.next_step_prompt = next_step_prompt
        return self

    def get_memory(self) -> Memory:
        return self.memory

    def set_memory(self, memory: Memory) -> 'BaseAgent':
        self.memory = memory
        return self

    def get_llm(self) -> Optional[LLM]:
        return self.llm

    def set_llm(self, llm: LLM) -> 'BaseAgent':
        self.llm = llm
        return self

    def get_context(self) -> Optional[AgentContext]:
        return self.context

    def set_context(self, context: AgentContext) -> 'BaseAgent':
        self.context = context
        return self

    def get_state(self) -> AgentState:
        return self.state

    def set_state(self, state: AgentState) -> 'BaseAgent':
        self.state = state
        return self

    def get_max_steps(self) -> int:
        return self.max_steps

    def set_max_steps(self, max_steps: int) -> 'BaseAgent':
        self.max_steps = max_steps
        return self

    def get_current_step(self) -> int:
        return self.current_step

    def set_current_step(self, current_step: int) -> 'BaseAgent':
        self.current_step = current_step
        return self

    def get_duplicate_threshold(self) -> int:
        return self.duplicate_threshold

    def set_duplicate_threshold(self, duplicate_threshold: int) -> 'BaseAgent':
        self.duplicate_threshold = duplicate_threshold
        return self

    def get_printer(self) -> Optional[Printer]:
        return self.printer

    def set_printer(self, printer: Printer) -> 'BaseAgent':
        self.printer = printer
        return self

    def get_digital_employee_prompt(self) -> Optional[str]:
        return self.digital_employee_prompt

    def set_digital_employee_prompt(self, digital_employee_prompt: str) -> 'BaseAgent':
        self.digital_employee_prompt = digital_employee_prompt
        return self