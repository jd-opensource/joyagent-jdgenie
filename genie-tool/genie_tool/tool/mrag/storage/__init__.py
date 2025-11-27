"""
存储模块

该模块负责各种数据的存储接口，包括向量数据库和数据库：
- Qdrant向量数据库操作
- 存储接口抽象
"""

from .vector_store import VectorStore

__all__ = [
    'VectorStore',
]
