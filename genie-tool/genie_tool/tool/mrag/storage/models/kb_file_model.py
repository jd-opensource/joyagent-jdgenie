from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KBFileModel(BaseModel):
    kb_id: Optional[str] = None
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    title: Optional[str] = None
    task_id: Optional[str] = None
    file_ext: Optional[str] = None
    source_type: Optional[str] = None
    task_status: Optional[dict] = None
    file_status: Optional[str] = None
    doc_count: Optional[int] = None
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    deleted: Optional[int] = None
    creator: Optional[str] = None
