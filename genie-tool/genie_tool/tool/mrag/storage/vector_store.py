"""
向量数据库接口模块

该模块提供向量数据库操作的统一接口：
- 向量的增删改查
- 批量向量操作
- 相似度检索
- 索引管理
- 集合（Collection）管理

主要功能：
1. 向量数据库连接和配置
2. 向量数据的CRUD操作
3. 高效的批量插入
4. 向量相似度搜索
5. 过滤条件查询
6. 混合搜索（文本+图像+页面）
"""

from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Tuple, Optional
import threading

from .config_manager import VectorStoreConfig
from .vector_store_factory import VectorStoreFactory
from ..utils.logger_utils import logger


class VectorStore:
    """
    向量存储统一接口类

    提供对文本、图像和页面向量存储的统一访问接口，使用懒加载模式。
    
    使用线程安全的单例模式实现，确保全局只有一个实例。
    """
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, store_type: Optional[str] = None):
        """
        单例模式实现 - 创建或返回现有实例
        
        Args:
            store_type: 存储类型，如果为 None 则从配置中读取
            
        Returns:
            VectorStore: 单例实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(VectorStore, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, store_type: Optional[str] = None):
        """
        初始化向量存储 - 只在第一次创建时执行

        Args:
            store_type: 存储类型，如果为 None 则从配置中读取
        """
        # 确保只初始化一次
        if self._initialized:
            return
            
        self.config = VectorStoreConfig()
        self.store_type = store_type or self.config.store_type

        # 懒加载属性
        self._base_store = None
        self._text_store = None
        self._image_store = None
        self._page_store = None
        
        self._initialized = True

        logger.debug(f"VectorStore initialized with type: {self.store_type}")

    @property
    def base_store(self):
        """基础向量数据库实例（懒加载）"""
        if self._base_store is None:
            self._base_store = VectorStoreFactory.create_vector_store(self.store_type)
            logger.info(f"Created base vector store: {self.store_type}")
        return self._base_store

    @property
    def text_store(self):
        """文本向量存储实例（懒加载）"""
        if self._text_store is None:
            logger.info("Init text store")
            self._text_store = VectorStoreFactory.create_text_store(
                collection_name=self.config.text_collection,
                vector_size=self.config.text_dimension,
                store_type=self.store_type,
                vector_store=self.base_store
            )
            logger.debug("Created text vector store")
        return self._text_store

    @property
    def image_store(self):
        """图像向量存储实例（懒加载）"""
        if self._image_store is None:
            self._image_store = VectorStoreFactory.create_image_store(
                collection_name=self.config.image_collection,
                vector_size=self.config.image_dimension,
                index_fields=["kb_id", "doc_id", "image_id"],
                store_type=self.store_type,
                vector_store=self.base_store
            )
            logger.debug("Created image vector store")
        return self._image_store

    @property
    def page_store(self):
        """页面向量存储实例（懒加载）"""
        if self._page_store is None:
            self._page_store = VectorStoreFactory.create_image_store(
                collection_name=self.config.page_collection,
                vector_size=self.config.page_dimension,
                index_fields=["kb_id", "page_id", "doc_id", "chunk_id"],
                store_type=self.store_type,
                vector_store=self.base_store
            )
            logger.debug("Created page vector store")
        return self._page_store

    # ==================== 集合管理 ====================

    def create_all_collections(self):
        """创建所有向量集合"""
        try:
            self.text_store.create_collection()
            logger.info("文本向量集合创建成功")
        except Exception as e:
            logger.error(f"文本向量集合创建失败: {e}")

        try:
            self.image_store.create_collection()
            logger.info("图像向量集合创建成功")
        except Exception as e:
            logger.error(f"图像向量集合创建失败: {e}")

        try:
            self.page_store.create_collection()
            logger.info("页面向量集合创建成功")
        except Exception as e:
            logger.error(f"页面向量集合创建失败: {e}")

    def drop_all_collections(self):
        """删除所有向量集合"""
        try:
            self.text_store.drop_collection()
            logger.info("文本向量集合删除成功")
        except Exception as e:
            logger.error(f"文本向量集合删除失败: {e}")

        try:
            self.image_store.drop_collection()
            logger.info("图像向量集合删除成功")
        except Exception as e:
            logger.error(f"图像向量集合删除失败: {e}")

        try:
            self.page_store.drop_collection()
            logger.info("页面向量集合删除成功")
        except Exception as e:
            logger.error(f"页面向量集合删除失败: {e}")

    # ==================== 获取存储实例 ====================

    def get_text_store(self):
        """获取文本向量存储实例"""
        return self.text_store

    def get_image_store(self):
        """获取图像向量存储实例"""
        return self.image_store

    def get_page_store(self):
        """获取页面向量存储实例"""
        return self.page_store

    # ==================== 添加向量 ====================

    def add_text_chunks(self, text_chunks: List[Dict]):
        """
        添加文本块到向量数据库

        Args:
            text_chunks: 文档块列表，每个块包含以下字段：
                - kb_id: 知识库ID (str)
                - doc_id: 文档ID (str)
                - chunk_id: 文档块ID (str)
                - page_no: 页码 (int, Optional)
                - page_chunk_id: 页内块ID (int, Optional)
                - text: 文本内容 (str)
                - vector: 向量数据 (List[float])
                - sparse_vector: 稀疏向量数据 (Dict[str, int])
        """
        return self.text_store.add_docs(text_chunks)

    def add_image_chunks(self, image_chunks: List[Dict]):
        """
        添加图像块到向量数据库

        Args:
            image_chunks: 图像块列表，每个块包含以下字段：
                - kb_id: 知识库ID (str)
                - doc_id: 文档ID (str)
                - image_id: 图像ID (str)
                - vector: 向量数据 (List[float])
        """
        return self.image_store.add_images(image_chunks)

    def add_page_chunks(self, page_chunks: List[Dict]):
        """
        添加页面块到向量数据库

        Args:
            page_chunks: 页面块列表，每个块包含以下字段：
                - kb_id: 知识库ID (str)
                - page_id: 页面ID (str)
                - doc_id: 文档ID (str)
                - chunk_id: 块ID (str)
                - vector: 向量数据 (List[float])
        """
        return self.page_store.add_images(page_chunks)

    # ==================== 搜索向量 ====================

    def search_text_vector(self,
                           query_vectors: List[list[float]],
                           limit: int = 10,
                           score_threshold: float = 0.0,
                           filter_conditions: Optional[Dict] = None) -> list[list[dict]]:
        """
        搜索文本向量

        Args:
            query_vectors: 查询向量
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件，如 {"kb_id": 1, "doc_id": 2}

        Returns:
            List[Dict]: 搜索结果列表，每个结果包含id, score, payload等
        """
        return self.text_store.search_vector(
            query_vectors=query_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def search_image_vector(self,
                            query_vectors: List[list[float]],
                            limit: int = 10,
                            score_threshold: float = 0.0,
                            filter_conditions: Optional[Dict] = None):
        """
        搜索图像向量

        Args:
            query_vectors: 查询向量
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        return self.image_store.search_vector(
            query_vectors=query_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def keyword_search(self,
                       queries: List[str],
                       sparse_vectors: Optional[List[Dict]] = None,
                       limit: int = 10,
                       score_threshold: float = 0.0,
                       filter_conditions: Optional[Dict] = None):
        """
        关键词搜索

        Args:
            queries: 查询关键词
            sparse_vectors: 稀疏向量查询
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        return self.text_store.keyword_search(
            queries=queries,
            sparse_vectors=sparse_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def search_page_vector(self,
                           query_vectors: List[list[float]],
                           limit: int = 10,
                           score_threshold: float = 0.0,
                           filter_conditions: Optional[Dict] = None):
        """
        搜索页面向量

        Args:
            query_vectors: 查询向量
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            List[Dict]: 搜索结果列表
        """
        return self.page_store.search_vector(
            query_vectors=query_vectors,
            limit=limit,
            score_threshold=score_threshold,
            filter_conditions=filter_conditions
        )

    def hybrid_search(self,
                      text_vectors: Optional[List[List[float]]],
                      image_vectors: Optional[List[List[float]]],
                      page_vectors: Optional[List[List[float]]],
                      limit: int = 10,
                      score_threshold: float = 0.0,
                      filter_conditions: Optional[Dict] = None):
        """
        混合搜索 - 并发执行三个维度的向量检索

        Args:
            text_vectors: 文本查询向量
            image_vectors: 图像查询向量
            page_vectors: 页面查询向量
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            Tuple[List[Dict], List[Dict], List[Dict]]: (文本结果, 图像结果, 页面结果)
        """

        def search_text():
            """文本向量搜索任务"""
            if text_vectors is None:
                return []
            return self.search_text_vector(
                query_vectors=text_vectors,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )

        def search_image():
            """图像向量搜索任务"""
            if image_vectors is None:
                return []
            return self.search_image_vector(
                query_vectors=image_vectors,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )

        def search_page():
            """页面向量搜索任务"""
            if page_vectors is None:
                return []
            return self.search_page_vector(
                query_vectors=page_vectors,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )

        # 使用线程池并发执行三个搜索任务
        with ThreadPoolExecutor(max_workers=3) as executor:
            # 提交所有搜索任务
            text_future = executor.submit(search_text)
            image_future = executor.submit(search_image)
            page_future = executor.submit(search_page)

            # 等待所有任务完成并获取结果
            text_results = text_future.result()
            image_results = image_future.result()
            page_results = page_future.result()

        return text_results, image_results, page_results

    # ==================== 删除向量 ====================

    def delete_text_by_kb_id(self, kb_id: str):
        """根据知识库ID删除文本向量"""
        return self.text_store.delete_by_kb_id(kb_id)

    def delete_text_by_doc_ids(self, doc_ids: List[int]):
        """根据文档ID列表删除文本向量"""
        return self.text_store.delete_by_doc_ids(doc_ids)

    def delete_text_by_chunk_ids(self, chunk_ids: List[int]):
        """根据文档块ID列表删除文本向量"""
        return self.text_store.delete_by_chunk_ids(chunk_ids)

    def delete_image_by_kb_id(self, kb_id: str):
        """根据知识库ID删除图像向量"""
        return self.image_store.delete_by_kb_id(kb_id)

    def delete_image_by_doc_ids(self, doc_ids: List[int]):
        """根据文档ID列表删除图像向量"""
        return self.image_store.delete_by_doc_ids(doc_ids)

    def delete_page_by_kb_id(self, kb_id: str):
        """根据知识库ID删除页面向量"""
        return self.page_store.delete_by_kb_id(kb_id)

    def delete_page_by_doc_ids(self, doc_ids: List[int]):
        """根据文档ID列表删除页面向量"""
        return self.page_store.delete_by_doc_ids(doc_ids)

    # ==================== 集合信息 ====================

    def get_text_collection_info(self):
        """获取文本集合信息"""
        try:
            return self.base_store.get_collection_info(self.config.text_collection)
        except Exception as e:
            logger.error(f"获取文本集合信息失败: {e}")
            return {'error': str(e)}

    def get_image_collection_info(self):
        """获取图像集合信息"""
        try:
            return self.base_store.get_collection_info(self.config.image_collection)
        except Exception as e:
            logger.error(f"获取图像集合信息失败: {e}")
            return {'error': str(e)}

    def get_page_collection_info(self):
        """获取页面集合信息"""
        try:
            return self.base_store.get_collection_info(self.config.page_collection)
        except Exception as e:
            logger.error(f"获取页面集合信息失败: {e}")
            return {'error': str(e)}

    def count_text_points(self, filter_conditions: Optional[Dict] = None):
        """统计文本向量点数量"""
        return self.base_store.count_vectors(self.config.text_collection, filter_conditions)

    def count_image_points(self, filter_conditions: Optional[Dict] = None):
        """统计图像向量点数量"""
        return self.base_store.count_vectors(self.config.image_collection, filter_conditions)

    def count_page_points(self, filter_conditions: Optional[Dict] = None):
        """统计页面向量点数量"""
        return self.base_store.count_vectors(self.config.page_collection, filter_conditions)

    def delete_by_file_ids(self, kb_id: str, file_ids: List[str]):
        self.text_store.delete_by_file_ids(kb_id, file_ids)
        self.image_store.delete_by_file_ids(kb_id, file_ids)
        self.page_store.delete_by_file_ids(kb_id, file_ids)