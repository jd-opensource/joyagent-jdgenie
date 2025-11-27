"""
向量数据库抽象基类模块

定义向量数据库的通用接口，支持不同的向量数据库实现：
- Qdrant
- Chroma
- Pinecone
- Weaviate
- 等其他向量数据库

架构设计：
1. BaseVectorStore - 核心向量数据库接口，定义所有底层操作
2. BaseCollectionVectorStore - 向量集合包装器基类，适用于所有类型（文本、图像、页面等）

主要功能：
1. 定义统一的向量数据库操作接口
2. 提供可扩展的架构设计
3. 支持插件化的数据库实现
4. 通过统一基类避免代码重复
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class BaseVectorStore(ABC):
    """向量数据库抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化向量数据库
        
        Args:
            config: 数据库配置
        """
        self.config = config

    @abstractmethod
    def create_collection(self, collection_name: str, **kwargs) -> bool:
        """
        创建集合
        
        Args:
            collection_name: 集合名称
            **kwargs: 其他参数（如向量维度、距离度量等）
            
        Returns:
            bool: 是否创建成功
        """
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """
        检查集合是否存在
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 集合是否存在
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    def add_vectors(self,
                    collection_name: str,
                    vectors: List[List[float]],
                    payloads: List[Dict],
                    sparse_vectors: Optional[List[Dict]] = None,
                    ids: Optional[List[str]] = None) -> bool:
        """
        添加向量到集合
        
        Args:
            collection_name: 集合名称
            vectors: 向量列表
            sparse_vectors: 稀疏向量列表
            payloads: 载荷数据列表
            ids: 向量ID列表，如果为None则自动生成
            
        Returns:
            bool: 是否添加成功
        """
        pass

    @abstractmethod
    def search_vectors(self,
                       collection_name: str,
                       query_vectors: List[List[float]],
                       limit: int = 10,
                       score_threshold: float = 0.0,
                       filter_conditions: Optional[Dict] = None) -> List[List[Dict]]:
        """
        搜索相似向量
        
        Args:
            collection_name: 集合名称
            query_vectors: 查询向量
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件
            
        Returns:
            List[Dict]: 搜索结果列表，每个结果包含id, score, payload等
        """
        pass

    @abstractmethod
    def keyword_search(self,
                       collection_name: str,
                       queries: List[str],
                       sparse_vectors: Optional[List[Dict]] = None,
                       limit: int = 10,
                       score_threshold: float = 0.0,
                       filter_conditions: Optional[Dict] = None) -> List[List[Dict]]:
        """
        关键词搜索

        Args:
            collection_name: 集合名称
            queries: 查询关键词
            sparse_vectors: 稀疏向量查询
            limit: 返回结果数量限制
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            List[Dict]: 搜索结果列表，每个结果包含id, score, payload等
        """
        pass

    @abstractmethod
    def delete_vectors(self,
                       collection_name: str,
                       filter_conditions: Dict) -> bool:
        """
        根据条件删除向量
        
        Args:
            collection_name: 集合名称
            filter_conditions: 删除条件
            
        Returns:
            bool: 是否删除成功
        """
        pass

    @abstractmethod
    def count_vectors(self,
                      collection_name: str,
                      filter_conditions: Optional[Dict] = None) -> int:
        """
        统计向量数量
        
        Args:
            collection_name: 集合名称
            filter_conditions: 过滤条件
            
        Returns:
            int: 向量数量
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        获取集合信息
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Dict: 集合信息
        """
        pass

    @abstractmethod
    def create_index(self,
                     collection_name: str,
                     field_name: str,
                     field_type: str) -> bool:
        """
        创建索引
        
        Args:
            collection_name: 集合名称
            field_name: 字段名称
            field_type: 字段类型
            
        Returns:
            bool: 是否创建成功
        """
        pass


class BaseCollectionVectorStore(ABC):
    """
    向量集合存储抽象基类

    这是一个通用的包装器基类，适用于所有类型的向量存储（文本、图像、页面等）。
    所有实际操作都委托给 BaseVectorStore 实例。
    """

    def __init__(self,
                 vector_store: BaseVectorStore,
                 collection_name: str,
                 vector_key: str = "vector",
                 embedding_size: int = 768,
                 index_fields: Optional[List[str]] = None):
        """
        初始化向量集合存储

        Args:
            vector_store: 向量数据库实例
            collection_name: 集合名称
            vector_key: 向量键名
            embedding_size: 向量维度
            index_fields: 索引字段列表
        """
        self.vector_store = vector_store
        self.collection_name = collection_name
        self.vector_key = vector_key
        self.embedding_size = embedding_size
        self.index_fields = index_fields or ["kb_id", "doc_id"]

    @abstractmethod
    def create_collection(self) -> bool:
        """创建向量集合"""
        pass

    @abstractmethod
    def drop_collection(self) -> bool:
        """删除向量集合"""
        pass

    @abstractmethod
    def search_vector(self,
                      query_vectors: List[list[float]],
                      limit: int = 10,
                      score_threshold: float = 0.0,
                      filter_conditions: Optional[Dict] = None) -> List[List[Dict]]:
        """搜索相似向量"""
        pass

    @abstractmethod
    def delete_by_kb_id(self, kb_id: str) -> bool:
        """根据知识库ID删除向量"""
        pass

    @abstractmethod
    def delete_by_doc_ids(self, doc_ids: List[int]) -> bool:
        """根据文档ID列表删除向量"""
        pass

    @abstractmethod
    def delete_by_key(self, key: str, values: List[str]) -> bool:
        """根据键值删除向量"""
        pass

    def delete_by_file_ids(self, kb_id: str, file_ids: List[str]) -> bool:
        """根据文件ID列表删除向量"""
        pass


BaseTextVectorStore = BaseCollectionVectorStore
BaseImageVectorStore = BaseCollectionVectorStore
