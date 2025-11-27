from abc import ABC
from typing import List

from PIL import Image


class BaseEmbedding(ABC):
    """Embedding基类"""

    def __init__(self):
        super().__init__()

    def _initialize(self, **kwargs):
        """
        初始化模型和相关配置
        子类必须实现此方法
        """
        pass

    def _load_model(self):
        """
        加载模型
        子类必须实现此方法
        """
        pass


class TextEmbedding(BaseEmbedding):
    """文本embedding类"""

    def __init__(self):
        super().__init__()

    def _encode_text_batch(self, texts: List[str]) -> list[any]:
        """
        批量编码文本为向量

        Args:
            texts: 文本列表

        Returns:
            向量数组，形状为 (len(texts), embedding_dim)
        """
        pass

    def encode_text_batch(self, texts: List[str]) -> list[any]:
        """
        批量编码文本为向量

        Args:
            texts: 文本列表

        Returns:
            向量数组，形状为 (len(texts), embedding_dim)
        """
        return self._encode_text_batch(texts)


class ImageEmbedding(TextEmbedding):
    """图像embedding类"""

    def __init__(self):
        super().__init__()

    def _encode_image_batch(self, images: List[Image.Image]) -> list[list[float]]:
        """
        批量编码图片为向量

        Args:
            images: 图片列表

        Returns:
            向量数组，形状为 (len(images), embedding_dim)
        """
        pass

    def encode_image_batch(self, images: List[Image.Image]) -> list[any]:
        """
        批量编码图片为向量

        Args:
            images: 图片列表

        Returns:
            向量数组，形状为 (len(images), embedding_dim)
        """
        return self._encode_image_batch(images)
