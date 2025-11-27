import os
from typing import List

import dotenv
from loguru import logger
from openai import OpenAI

from .embedding import TextEmbedding

dotenv.load_dotenv()


class OpenAITextEmbedding(TextEmbedding):

    def _encode_text_batch(self, texts: List[str]) -> list[list[float]]:
        """
        批量编码文本为向量

        Args:
            texts: 文本列表

        Returns:
            向量数组，形状为 (len(texts), embedding_dim)
        """
        if not texts:
            return []

        max_text_length = int(os.getenv("TEXT_EMBEDDING_MAX_TEXT_LENGTH", 8000))
        texts = [text[:max_text_length] for text in texts]

        try:
            client = OpenAI(
                base_url=os.getenv("TEXT_EMBEDDING_BASE_URL"),
                api_key=os.getenv("TEXT_EMBEDDING_API_KEY"),
            )

            batch_size = 10
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                response = client.embeddings.create(
                    model=os.getenv("TEXT_EMBEDDING_MODEL_NAME"),
                    input=batch_texts,
                    timeout=int(os.getenv("API_TIMEOUT", 300)),
                )
                response_data = response.data
                if not response_data:
                    raise ValueError("文本编码失败: 未返回任何数据")

                for embedding in response_data:
                    embeddings.append(embedding.embedding)
            return embeddings

        except Exception as e:
            import traceback
            logger.error(f"文本编码失败: {e}\n{traceback.format_exc()}")
            raise Exception(f"文本编码失败: {e}") from e


def get_text_embedding_model() -> TextEmbedding:
    """获取文本embedding模型"""
    embedding_type = os.getenv("TEXT_EMBEDDING_TYPE")
    if embedding_type.lower() == "openai":
        return OpenAITextEmbedding()
    else:
        raise ValueError(f"不支持的文本embedding模型: {embedding_type}")
