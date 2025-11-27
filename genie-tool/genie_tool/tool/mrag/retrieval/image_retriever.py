"""
图像召回模块

该模块处理图像相关的召回功能：
- 文本到图像召回（t2i）
- 图像到图像召回（i2i）
- 多模态特征融合召回
- 图像内容理解召回

主要功能：
1. 文本描述匹配图像
2. 图像相似度检索
3. 图像特征提取和匹配
4. OCR文本与图像结合召回
5. 图像标签和元数据召回
6. 多尺度图像特征匹配
"""
from typing import Dict, Optional

from PIL import Image

from ..embedding.image_embedding import get_image_embedding_model
from ..storage import VectorStore


class ImageRetriever:
    """图像检索器类"""

    def __init__(self):
        self.embedding_model = get_image_embedding_model()
        self.vector_store = VectorStore()

    def text2image_search(self, kb_id: str, queries: list[str], limit: int = 10, score_threshold: float = 0.0,
                          filter_conditions: Optional[Dict] = None):
        """文本到图像检索"""
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        text_embeddings = self.embedding_model.encode_text_batch(queries)
        return self.vector_store.search_image_vector(
            query_vectors=text_embeddings,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def image2image_search(self,
                           kb_id: str, image: Image.Image, limit: int = 10, score_threshold: float = 0.0,
                           filter_conditions: Optional[Dict] = None):
        """图像检索"""
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        image_embeddings = self.embedding_model.encode_image_batch([image])
        return self.vector_store.search_image_vector(
            query_vectors=image_embeddings,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )[0]

    def text2page_search(self, kb_id: str, queries: list[str], limit: int = 10, score_threshold: float = 0.0,
                         filter_conditions: Optional[Dict] = None):
        """文本到页面检索"""
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        text_embeddings = self.embedding_model.encode_text_batch(queries)
        return self.vector_store.search_page_vector(
            query_vectors=text_embeddings,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def image2page_search(self,
                          kb_id: str, image: Image.Image, limit: int = 10, score_threshold: float = 0.0,
                          filter_conditions: Optional[Dict] = None):
        """图像到页面检索"""
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        image_embeddings = self.embedding_model.encode_image_batch([image])
        return self.vector_store.search_page_vector(
            query_vectors=image_embeddings,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )
