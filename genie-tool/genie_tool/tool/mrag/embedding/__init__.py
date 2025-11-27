"""
Embedding模块

该模块负责各种类型内容的向量化：
- 文本embedding
- 多模态embedding
"""

from .embedding import BaseEmbedding
from .image_embedding import ImageEmbedding
from .text_embedding import TextEmbedding

__all__ = ["BaseEmbedding", "TextEmbedding", "ImageEmbedding"]
