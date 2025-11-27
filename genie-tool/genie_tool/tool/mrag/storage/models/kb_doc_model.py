from typing import Optional

from pydantic import BaseModel

class KBDocModel(BaseModel):
    kb_id: str
    doc_id: Optional[str]
    text: Optional[str]
    chunk_type: Optional[str]
    file_id: Optional[str]
    title: Optional[str]
    file_url: Optional[str]
    parent_id: Optional[str]
    deleted: Optional[int]
    create_time: Optional[str]
    modify_time: Optional[str]
    creator: Optional[str]
    modifier: Optional[str]
