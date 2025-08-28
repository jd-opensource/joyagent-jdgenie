"""
Assistant返回DTO
"""
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Plan(BaseModel):
    """计划"""
    title: Optional[str] = Field(None, description="标题")
    stages: Optional[List[str]] = Field(None, description="阶段列表")
    steps: Optional[List[str]] = Field(None, description="步骤列表")
    step_status: Optional[List[str]] = Field(None, description="步骤状态列表")
    notes: Optional[List[str]] = Field(None, description="备注列表")


class ToolResult(BaseModel):
    """工具结果"""
    tool_name: Optional[str] = Field(None, description="工具名称")
    tool_param: Optional[Dict[str, Any]] = Field(None, description="工具参数")
    tool_result: Optional[str] = Field(None, description="工具结果")


class AgentResponse(BaseModel):
    """Assistant返回"""
    request_id: Optional[str] = Field(None, description="请求ID")
    message_id: Optional[str] = Field(None, description="消息ID")
    is_final: Optional[bool] = Field(None, description="是否最终结果")
    message_type: Optional[str] = Field(None, description="消息类型")
    digital_employee: Optional[str] = Field(None, description="数字员工")
    message_time: Optional[str] = Field(None, description="消息时间")
    plan_thought: Optional[str] = Field(None, description="计划思考")
    plan: Optional[Plan] = Field(None, description="计划")
    task: Optional[str] = Field(None, description="任务")
    task_summary: Optional[str] = Field(None, description="任务总结")
    tool_thought: Optional[str] = Field(None, description="工具思考")
    tool_result: Optional[ToolResult] = Field(None, description="工具结果")
    result_map: Optional[Dict[str, Any]] = Field(None, description="结果映射")
    result: Optional[str] = Field(None, description="结果")
    finish: Optional[bool] = Field(None, description="是否完成")
    ext: Optional[Dict[str, str]] = Field(None, description="扩展信息")

    @staticmethod
    def format_steps(plan: Plan) -> Plan:
        """格式化步骤"""
        new_plan = Plan(
            title=plan.title,
            steps=[],
            stages=[],
            step_status=[],
            notes=[]
        )
        
        pattern = re.compile(r"执行顺序(\d+)\.\s?([\\w\\W]*)\s?[：:](.*)") 
        
        for i, step in enumerate(plan.steps or []):
            if i < len(plan.step_status or []):
                new_plan.step_status.append(plan.step_status[i])
            if i < len(plan.notes or []):
                new_plan.notes.append(plan.notes[i])

            matcher = pattern.match(step)
            if matcher:
                new_plan.steps.append(matcher.group(3).strip())
                new_plan.stages.append(matcher.group(2).strip())
            else:
                new_plan.steps.append(step)
                new_plan.stages.append("")

        return new_plan