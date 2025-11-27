from typing import Optional, List

from pydantic import BaseModel, Field


class ImageChunkModel(BaseModel):
    kb_id: str = Field(..., description="知识库的ID")
    page_id: Optional[str] = Field(None, description="来源文档的ID")
    doc_id: Optional[str] = Field(None, description="所属页的chunk_id")
    chunk_id: Optional[str] = Field(None, description="文档的块ID")
    page_chunk_id: Optional[str] = Field(None, description="page_chunk_id")
    page_no: Optional[str] = Field(None, description="文档的页码")
    tags: Optional[List[str]] = Field(default_factory=list, description="文档的标签")
    caption: Optional[str] = Field(None, description="图片的标题")
    vector: Optional[List[float]] = Field(None, description="图片的向量表示")
    doc: Optional[str] = Field(None, description="文档的内容")
    image_url: Optional[str] = Field(None, description="图片的URL")
    md5sum: Optional[str] = Field(None, description="图片的MD5值")
    image_type: Optional[str] = Field(None, description="图片的类型")

    class Config:
        extra = "allow"
