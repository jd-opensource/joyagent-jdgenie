"""
计划类
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Plan(BaseModel):
    """计划类"""
    title: Optional[str] = Field(None, description="计划标题")
    steps: Optional[List[str]] = Field(default_factory=list, description="计划步骤列表")
    step_status: Optional[List[str]] = Field(default_factory=list, description="步骤状态列表")
    notes: Optional[List[str]] = Field(default_factory=list, description="步骤备注列表")

    @classmethod
    def create(cls, title: str, steps: List[str]) -> "Plan":
        """创建新计划"""
        status = ["not_started"] * len(steps)
        notes = [""] * len(steps)

        return cls(
            title=title,
            steps=steps,
            step_status=status,
            notes=notes
        )

    def update(self, title: Optional[str] = None, new_steps: Optional[List[str]] = None) -> None:
        """更新计划"""
        if title is not None:
            self.title = title

        if new_steps is not None:
            new_statuses = []
            new_notes = []

            for i, new_step in enumerate(new_steps):
                if (i < len(self.steps) and 
                    new_step == self.steps[i]):
                    # 保持原有状态和备注
                    new_statuses.append(self.step_status[i])
                    new_notes.append(self.notes[i])
                else:
                    # 新步骤使用默认状态和空备注
                    new_statuses.append("not_started")
                    new_notes.append("")

            self.steps = new_steps
            self.step_status = new_statuses
            self.notes = new_notes

    def update_step_status(self, step_index: int, status: Optional[str] = None, note: Optional[str] = None) -> None:
        """更新步骤状态"""
        if step_index < 0 or step_index >= len(self.steps):
            raise ValueError(f"Invalid step index: {step_index}")

        if status is not None:
            self.step_status[step_index] = status

        if note is not None:
            self.notes[step_index] = note

    def get_current_step(self) -> str:
        """获取当前步骤"""
        for i, status in enumerate(self.step_status):
            if status == "in_progress":
                return self.steps[i]
        return ""

    def step_plan(self) -> None:
        """更新当前task为 completed，下一个task为 in_progress"""
        if not self.steps:
            return

        if not self.get_current_step():
            self.update_step_status(0, "in_progress", "")
            return

        for i, status in enumerate(self.step_status):
            if status == "in_progress":
                self.update_step_status(i, "completed", "")
                if i + 1 < len(self.steps):
                    self.update_step_status(i + 1, "in_progress", "")
                break

    def format(self) -> str:
        """格式化计划显示"""
        result = []

        # 添加计划标题
        result.append(f"Plan: {self.title}")
        # 添加步骤列表
        result.append("Steps:")
        
        for i, step in enumerate(self.steps):
            status = self.step_status[i]
            note = self.notes[i]
            result.append(f"{i + 1}. [{status}] {step}")

            if note:
                result.append(f"   Notes: {note}")

        return "\n".join(result)