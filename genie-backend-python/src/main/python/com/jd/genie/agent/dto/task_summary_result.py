"""
任务总结结果DTO
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from .file import File


class TaskSummaryResult(BaseModel):
    """任务总结结果"""
    task_summary: Optional[str] = Field(None, description="任务总结")
    files: Optional[List[File]] = Field(None, description="文件列表")