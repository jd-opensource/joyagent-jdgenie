"""
召回模块

该模块负责多模态内容的召回功能：
- 文本到文本召回
- 文本到图像召回
- 图像到图像召回
- 图知识召回
"""

from .image_retriever import ImageRetriever
from .retriever import BaseRetriever
from .text_retriever import TextRetriever

__all__ = ["BaseRetriever", "TextRetriever", "ImageRetriever"]
