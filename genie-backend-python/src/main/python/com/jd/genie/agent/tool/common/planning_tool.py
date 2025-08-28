"""
Planning tool for creating and managing plans for solving complex tasks.
计划工具类
"""
import logging
from typing import Any, Callable, Dict, List, Optional

from ..base_tool import BaseTool
from ...dto.plan import Plan
from ...util.dependency_container import DependencyContainer

logger = logging.getLogger(__name__)


class PlanningTool(BaseTool):
    """Planning tool for creating and managing plans."""
    
    def __init__(self):
        self.agent_context = None
        self.command_handlers: Dict[str, Callable[[Dict[str, Any]], str]] = {
            "create": self._create_plan,
            "update": self._update_plan,
            "mark_step": self._mark_step,
            "finish": self._finish_plan
        }
        self.plan: Optional[Plan] = None
    
    def get_name(self) -> str:
        return "planning"
    
    def get_description(self) -> str:
        desc = ("这是一个计划工具，可让代理创建和管理用于解决复杂任务的计划。\n"
                "该工具提供创建计划、更新计划步骤和跟踪进度的功能。\n"
                "使用中文回答")
        config = DependencyContainer.get_config()
        return config.plan_tool_desc if config.plan_tool_desc else desc
    
    def to_params(self) -> Dict[str, Any]:
        config = DependencyContainer.get_config()
        if config.plan_tool_params:
            return config.plan_tool_params
        
        return self._get_parameters()
    
    def _get_parameters(self) -> Dict[str, Any]:
        """Get the tool parameters schema."""
        return {
            "type": "object",
            "properties": self._get_properties(),
            "required": ["command"]
        }
    
    def _get_properties(self) -> Dict[str, Any]:
        """Get the properties for the tool parameters."""
        return {
            "command": self._get_command_property(),
            "title": self._get_title_property(),
            "steps": self._get_steps_property(),
            "step_index": self._get_step_index_property(),
            "step_status": self._get_step_status_property(),
            "step_notes": self._get_step_notes_property()
        }
    
    def _get_command_property(self) -> Dict[str, Any]:
        """Get command property definition."""
        return {
            "type": "string",
            "enum": ["create", "update", "mark_step", "finish"],
            "description": "The command to execute. Available commands: create, update, mark_step, finish"
        }
    
    def _get_title_property(self) -> Dict[str, Any]:
        """Get title property definition."""
        return {
            "type": "string",
            "description": "Title for the plan. Required for create command, optional for update command."
        }
    
    def _get_steps_property(self) -> Dict[str, Any]:
        """Get steps property definition."""
        return {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of plan steps. Required for create command, optional for update command."
        }
    
    def _get_step_index_property(self) -> Dict[str, Any]:
        """Get step index property definition."""
        return {
            "type": "integer",
            "description": "Index of the step to update (0-based). Required for mark_step command."
        }
    
    def _get_step_status_property(self) -> Dict[str, Any]:
        """Get step status property definition."""
        return {
            "type": "string",
            "enum": ["not_started", "in_progress", "completed", "blocked"],
            "description": "Status to set for a step. Used with mark_step command."
        }
    
    def _get_step_notes_property(self) -> Dict[str, Any]:
        """Get step notes property definition."""
        return {
            "type": "string",
            "description": "Additional notes for a step. Optional for mark_step command."
        }
    
    def execute(self, input_data: Any) -> Any:
        if not isinstance(input_data, dict):
            raise ValueError("Input must be a dictionary")
        
        params = input_data
        command = params.get("command")
        
        if not command:
            raise ValueError("Command is required")
        
        handler = self.command_handlers.get(command)
        if handler:
            return handler(params)
        else:
            raise ValueError(f"Unknown command: {command}")
    
    def _create_plan(self, params: Dict[str, Any]) -> str:
        """Create a new plan."""
        title = params.get("title")
        steps = params.get("steps")
        
        if not title or not steps:
            raise ValueError("title and steps are required for create command")
        
        if self.plan is not None:
            raise ValueError("A plan already exists. Delete the current plan first.")
        
        self.plan = Plan.create(title, steps)
        return "我已创建plan"
    
    def _update_plan(self, params: Dict[str, Any]) -> str:
        """Update an existing plan."""
        title = params.get("title")
        steps = params.get("steps")
        
        if self.plan is None:
            raise ValueError("No plan exists. Create a plan first.")
        
        self.plan.update(title, steps)
        return "我已更新plan"
    
    def _mark_step(self, params: Dict[str, Any]) -> str:
        """Mark a step with a new status."""
        step_index = params.get("step_index")
        step_status = params.get("step_status")
        step_notes = params.get("step_notes")
        
        if self.plan is None:
            raise ValueError("No plan exists. Create a plan first.")
        
        if step_index is None:
            raise ValueError("step_index is required for mark_step command")
        
        self.plan.update_step_status(step_index, step_status, step_notes)
        
        return f"我已标记plan {step_index} 为 {step_status}"
    
    def _finish_plan(self, params: Dict[str, Any]) -> str:
        """Finish the plan by marking all steps as completed."""
        if self.plan is None:
            self.plan = Plan()
        else:
            for step_index in range(len(self.plan.steps)):
                self.plan.update_step_status(step_index, "completed", "")
        return "我已更新plan为完成状态"
    
    def step_plan(self) -> None:
        """Step the plan forward."""
        if self.plan:
            self.plan.step_plan()
    
    def get_format_plan(self) -> str:
        """Get the formatted plan string."""
        if self.plan is None:
            return "目前还没有Plan"
        return self.plan.format()
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context