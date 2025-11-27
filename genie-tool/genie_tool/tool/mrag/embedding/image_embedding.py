import os
from http import HTTPStatus
from typing import List

import requests
from PIL import Image

from .embedding import ImageEmbedding
from ..utils import image_utils
from ..utils.logger_utils import logger


class QwenVLEmbedding(ImageEmbedding):
    def __init__(self):
        super().__init__()
        self.timeout = int(os.getenv("API_TIMEOUT", 300))
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.model_name = "qwen2.5-vl-embedding"
        self.dashscope_base_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/multimodal-embedding/multimodal-embedding"
        if os.getenv("DASHSCOPE_MULTIMODAL_EMBEDDING_BASE_URL"):
            self.dashscope_base_url = os.getenv("DASHSCOPE_MULTIMODAL_EMBEDDING_BASE_URL")

        if os.getenv("DASHSCOPE_MULTIMODAL_EMBEDDING_MODEL_NAME"):
            self.model_name = os.getenv("DASHSCOPE_MULTIMODAL_EMBEDDING_MODEL_NAME")

    @staticmethod
    def _image_to_base64(image: Image.Image) -> str:
        """
        将PIL图像转换为base64编码字符串

        Args:
            image: PIL图像对象

        Returns:
            base64编码的图像字符串
        """
        return "data:image/png;base64," + image_utils.image_to_base64(image)

    def _encode_image(self, image: Image.Image) -> list[float]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        body = {
            "model": self.model_name,
            "input": {
                "contents": [{"image": self._image_to_base64(image)}]
            }
        }

        resp = requests.post(
            self.dashscope_base_url,
            headers=headers,
            json=body,
            timeout=self.timeout
        )
        if resp.status_code == HTTPStatus.OK:
            return resp.json()["output"]["embeddings"][0]['embedding']
        else:
            print(resp.text)
            return []

    def _encode_image_batch(self, images: List[Image.Image]) -> list[list[float]]:
        """
        批量编码图片为向量

        Args:
            images: 图片列表

        Returns:
            向量数组，形状为 (len(images), embedding_dim)
        """
        if not images:
            return []

        embeddings = []
        for image in images:
            embedding = self._encode_image(image)
            embeddings.append(embedding)
        return embeddings

    def _encode_text(self, text: str):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            contents = [{"text": text}]
            body = {
                "model": self.model_name,
                "input": {
                    "contents": contents
                }
            }

            resp = requests.post(
                self.dashscope_base_url,
                headers=headers,
                json=body,
                timeout=self.timeout
            )
            if resp.status_code == HTTPStatus.OK:

                output_data = resp.json()
                return output_data["output"]["embeddings"][0]["embedding"]

            else:
                logger.error(f"文本编码失败: {resp}")
                return []


        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise Exception(f"文本编码失败: {e}") from e

    def _encode_text_batch(self, texts: List[str]) -> list[list[float]]:
        """
        批量编码图片为向量

        Args:
            texts: 文本列表

        Returns:
            向量数组，形状为 (len(images), embedding_dim)
        """
        if not texts:
            return []
        embeddings = []
        for text in texts:
            embedding = self._encode_text(text)
            embeddings.append(embedding)
        return embeddings


def get_image_embedding_model() -> ImageEmbedding:
    """获取图像embedding模型"""
    image_embedding_type = os.getenv("IMAGE_EMBEDDING_TYPE")
    if image_embedding_type == "dashscope":
        return QwenVLEmbedding()
    else:
        raise ValueError(f"不支持的图像embedding模型: {image_embedding_type}")
