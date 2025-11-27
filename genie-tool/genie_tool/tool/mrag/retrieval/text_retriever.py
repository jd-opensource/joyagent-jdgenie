"""
文本召回模块

该模块专门处理文本到文本的召回功能：
- 关键词匹配召回
- 语义相似度召回
- 混合召回策略
- 多语言文本召回

主要功能：
1. BM25关键词匹配召回
2. 向量相似度召回
3. 混合召回算法（关键词+语义）
4. 文本预处理和查询扩展
5. 多语言支持
6. 召回结果去重和排序
"""

from typing import Dict, Optional

from ..embedding.bm25_embedding import get_bm25_embedding_model
from ..embedding.text_embedding import get_text_embedding_model
from ..storage import VectorStore
from ..utils.logger_utils import logger


class TextRetriever:
    """文本检索器类"""

    def __init__(self):
        self.embedding_model = get_text_embedding_model()
        self.vector_store = VectorStore()
        self.bm25_embedding_model = get_bm25_embedding_model()

    def vector_search(self, kb_id: str, queries: list[str], limit: int = 10, score_threshold: float = 0.0,
                      filter_conditions: Optional[Dict] = None
                      ) -> list[list[dict]]:
        """向量相似度召回 """
        logger.info(f"vector_search: {queries}, filter_conditions: {filter_conditions}")
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        logger.info(f"filter_conditions: {filter_conditions}")
        query_vectors = self.embedding_model.encode_text_batch(queries)
        # print(query_vectors)
        return self.vector_store.search_text_vector(
            query_vectors=query_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def sparse_search(self, kb_id: str, queries: list[str], limit: int = 10, score_threshold: float = 0.0,
                      filter_conditions: Optional[Dict] = None):
        """稀疏向量召回"""
        if not filter_conditions:
            filter_conditions = {}
        filter_conditions.update({"kb_id": kb_id})
        query_vectors = self.bm25_embedding_model.encode_text_batch(queries)
        print(query_vectors)
        return self.vector_store.keyword_search(
            queries=queries,
            sparse_vectors=query_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )
