"""
Plan solve handler implementation.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from ..agent_handler_service import AgentHandlerService
from ...agent.agent.agent_context import AgentContext
from ...agent.agent.executor_agent import ExecutorAgent
from ...agent.agent.planning_agent import PlanningAgent
from ...agent.agent.summary_agent import SummaryAgent
from ...agent.dto.file import File
from ...agent.dto.task_summary_result import TaskSummaryResult
from ...agent.enums.agent_state import AgentState
from ...agent.enums.agent_type import AgentType
from ...config.genie_config import GenieConfig
from ...model.req.agent_request import AgentRequest

logger = logging.getLogger(__name__)


class PlanSolveHandlerImpl(AgentHandlerService):
    """Implementation of plan-solve handler service."""
    
    def __init__(self, genie_config: GenieConfig):
        """
        Initialize with Genie configuration.
        
        Args:
            genie_config: Genie configuration instance
        """
        self.genie_config = genie_config
    
    async def handle(self, agent_context: AgentContext, request: AgentRequest) -> str:
        """
        Handle plan-solve agent processing.
        
        Args:
            agent_context: Agent context
            request: Agent request
            
        Returns:
            Processing result
        """
        planning = PlanningAgent(agent_context)
        executor = ExecutorAgent(agent_context)
        summary = SummaryAgent(agent_context)
        summary.system_prompt = summary.system_prompt.replace("{{query}}", request.query)
        
        planning_result = await planning.run(agent_context.query)
        step_idx = 0
        max_step_num = self.genie_config.planner_max_steps
        
        while step_idx <= max_step_num:
            planning_results = [
                f"你的任务是：{task.strip()}" 
                for task in planning_result.split("<sep>")
                if task.strip()
            ]
            
            agent_context.task_product_files.clear()
            
            if len(planning_results) == 1:
                executor_result = await executor.run(planning_results[0])
            else:
                executor_result = await self._execute_parallel_tasks(
                    planning_results, executor, agent_context
                )
            
            planning_result = await planning.run(executor_result)
            
            if planning_result == "finish":
                # Task successfully completed, summarize
                result = await summary.summary_task_result(
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
                break
            
            if (planning.state == AgentState.IDLE or 
                executor.state == AgentState.IDLE):
                await agent_context.printer.send("result", "达到最大迭代次数，任务终止。")
                break
                
            if (planning.state == AgentState.ERROR or 
                executor.state == AgentState.ERROR):
                await agent_context.printer.send("result", "任务执行异常，请联系管理员，任务终止。")
                break
                
            step_idx += 1
        
        return ""
    
    async def _execute_parallel_tasks(
        self,
        planning_results: List[str],
        executor: ExecutorAgent,
        agent_context: AgentContext
    ) -> str:
        """
        Execute multiple tasks in parallel.
        
        Args:
            planning_results: List of tasks to execute
            executor: Main executor agent
            agent_context: Agent context
            
        Returns:
            Combined result from all tasks
        """
        task_results: Dict[str, str] = {}
        memory_index = len(executor.memory.messages)
        slave_executors: List[ExecutorAgent] = []
        
        # Create tasks for parallel execution
        async def execute_task(task: str) -> None:
            slave_executor = ExecutorAgent(agent_context)
            slave_executor.state = executor.state
            slave_executor.memory.add_messages(executor.memory.messages)
            slave_executors.append(slave_executor)
            
            task_result = await slave_executor.run(task)
            task_results[task] = task_result
        
        # Execute tasks concurrently
        tasks = [execute_task(task) for task in planning_results]
        await asyncio.gather(*tasks)
        
        # Merge results back to main executor
        for slave_executor in slave_executors:
            for i in range(memory_index, len(slave_executor.memory.messages)):
                executor.memory.add_message(slave_executor.memory.messages[i])
            slave_executor.memory.clear()
            executor.state = slave_executor.state
        
        return "\n".join(task_results.values())
    
    def support(self, agent_context: AgentContext, request: AgentRequest) -> bool:
        """
        Check if this handler supports the given request.
        
        Args:
            agent_context: Agent context
            request: Agent request
            
        Returns:
            True if supports plan-solve agent type
        """
        return AgentType.PLAN_SOLVE.value == request.agent_type