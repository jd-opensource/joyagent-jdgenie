"""
基础检索器模块

该模块定义检索器的基础接口和通用功能：
- 检索器抽象基类
- 通用检索逻辑
- 检索结果处理
- 检索性能监控

主要功能：
1. 定义检索器标准接口
2. 提供通用检索流程
3. 检索结果格式化
4. 检索性能统计和优化
5. 缓存机制
"""
import concurrent.futures
import os

import requests

from .image_retriever import ImageRetriever
from .text_retriever import TextRetriever
from ..utils.logger_utils import logger


class BaseRetriever:
    """基础检索器抽象类"""

    def __init__(self):
        self._image_retriever = ImageRetriever()
        self._text_retriever = TextRetriever()

    def retrieval_by_texts(self, kb_id: str, queries: list[str]):

        tasks = []
        res = [[] for _ in range(len(queries))]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            task = executor.submit(self._text_retriever.vector_search, kb_id, queries,
                                   score_threshold=float(os.getenv("RETRIEVAL_TEXT_THRESHOLD")))
            tasks.append(task)
            task = executor.submit(self._text_retriever.sparse_search, kb_id, queries)
            tasks.append(task)
            task = executor.submit(self._image_retriever.text2image_search, kb_id, queries,
                                   score_threshold=float(os.getenv("RETRIEVAL_IMAGE_THRESHOLD")))
            tasks.append(task)
            task = executor.submit(self._image_retriever.text2page_search, kb_id, queries,
                                   score_threshold=float(os.getenv("RETRIEVAL_PAGE_THRESHOLD")))
            tasks.append(task)

            for task in concurrent.futures.as_completed(tasks):
                current_res = task.result()
                if current_res:
                    for i, query in enumerate(queries):
                        res[i].extend(current_res[i])

        return res

    def retrieval_image(self, image_path: str):
        pass

    def retrieval_lightrag(self, kb_id: str, queries: list[str]):
        url = f"{os.getenv('LIGHTRAG_SERVER_BASE_URL')}/query/data"

        data = {
            "query": "",
            "mode": "global",
            "top_k": 10
        }

        def make_query(query):
            data["query"] = query
            try:
                response = requests.post(url, json=data, timeout=300)
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
            except Exception as e:
                import traceback
                logger.error(traceback.format_exc())
                logger.error(f"LightRAG 请求失败: {e}")
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            tasks = [executor.submit(make_query, query) for query in queries]
            results = [task.result() for task in tasks]


        return results
