"""
事件结果DTO
"""
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from threading import Lock


class EventResult(BaseModel):
    """事件结果"""
    message_count: int = Field(default=0, description="增量消息计数")
    order_mapping: Dict[str, int] = Field(default_factory=dict, description="增量消息偏移量映射（从 1 开始）")
    init_plan: Optional[bool] = Field(None, description="增量计划-初始化标识")
    task_id: Optional[str] = Field(None, description="增量任务ID")
    task_order: int = Field(default=1, description="任务顺序")
    stream_task_message_type: List[str] = Field(
        default_factory=lambda: ["html", "markdown", "deep_search", "tool_thought"],
        description="增量任务-流式消息类型"
    )
    result_map: Dict[str, Any] = Field(default_factory=dict, description="全量结果（回放）")
    result_list: List[Any] = Field(default_factory=list, description="全量结果（重连）")

    class Config:
        # Allow extra fields for compatibility
        extra = "allow"

    def get_and_incr_order(self, key: str) -> int:
        """获取并递增顺序"""
        order = self.order_mapping.get(key)
        if order is None:
            self.order_mapping[key] = 1
            return 1
        self.order_mapping[key] = order + 1
        return order + 1

    def is_init_plan(self) -> bool:
        """增量计划-初始化标识"""
        if self.init_plan is None or self.init_plan is False:
            self.init_plan = True
            return True
        return False

    def get_task_id(self) -> str:
        """获取任务ID"""
        if self.task_id is None or self.task_id == "":
            self.task_id = str(uuid.uuid4())
        return self.task_id

    def renew_task_id(self) -> str:
        """更新任务ID"""
        self.task_order = 1
        self.task_id = str(uuid.uuid4())
        return self.task_id

    def get_result_map_task(self) -> Optional[List[Any]]:
        """获取结果映射任务"""
        if "tasks" in self.result_map:
            return self.result_map["tasks"]
        return None

    def set_result_map_task(self, task: List[Any]) -> None:
        """设置结果映射任务"""
        tasks = self.get_result_map_task()
        if tasks is None:
            tasks = [task]
            self.result_map["tasks"] = tasks
        else:
            tasks.append(task)

    def set_result_map_sub_task(self, sub_task: Any) -> None:
        """设置结果映射子任务"""
        tasks = self.get_result_map_task()
        if tasks is None:
            tasks = [[]]
            self.result_map["tasks"] = tasks
        
        sub_tasks = tasks[-1] if tasks else []
        if not isinstance(sub_tasks, list):
            sub_tasks = []
            tasks[-1] = sub_tasks
        
        sub_tasks.append(sub_task)