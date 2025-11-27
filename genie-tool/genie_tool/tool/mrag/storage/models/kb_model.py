from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KBModel(BaseModel):
    kb_id: str
    kb_name: Optional[str] = None
    kb_desc: Optional[str] = None
    chunk_type: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap_size: Optional[int] = None
    deleted: Optional[int] = None
    create_time: Optional[datetime] = None
    modify_time: Optional[datetime] = None
    creator: Optional[str] = None
