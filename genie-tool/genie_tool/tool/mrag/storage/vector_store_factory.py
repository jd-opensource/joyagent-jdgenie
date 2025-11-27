"""
向量存储工厂模块

提供向量数据库的工厂模式实现，支持：
- 动态选择不同的向量数据库实现
- 插件化的数据库扩展
- 统一的实例创建接口
"""

from typing import Dict, Any, Optional

from .base_vector_store import BaseTextVectorStore, BaseImageVectorStore
from .base_vector_store import BaseVectorStore
from .config_manager import VectorStoreConfig
from .qdrant_vector_store import (
    QdrantVectorStore,
    QdrantTextVectorStore,
    QdrantImageVectorStore
)
from ..utils.logger_utils import logger


class VectorStoreFactory:
    """向量存储工厂类"""

    # 注册的向量数据库实现
    _vector_stores = {
        'qdrant': QdrantVectorStore,
    }

    # 注册的文本向量存储实现
    _text_stores = {
        'qdrant': QdrantTextVectorStore,
    }

    # 注册的图像向量存储实现
    _image_stores = {
        'qdrant': QdrantImageVectorStore,
    }

    @classmethod
    def register_vector_store(cls, name: str, store_class: type):
        """
        注册新的向量数据库实现
        
        Args:
            name: 数据库名称
            store_class: 实现类
        """
        cls._vector_stores[name] = store_class
        logger.info(f"Registered vector store: {name}")

    @classmethod
    def register_text_store(cls, name: str, store_class: type):
        """
        注册新的文本向量存储实现
        
        Args:
            name: 存储名称
            store_class: 实现类
        """
        cls._text_stores[name] = store_class
        logger.info(f"Registered text store: {name}")

    @classmethod
    def register_image_store(cls, name: str, store_class: type):
        """
        注册新的图像向量存储实现
        
        Args:
            name: 存储名称
            store_class: 实现类
        """
        cls._image_stores[name] = store_class
        logger.info(f"Registered image store: {name}")

    @classmethod
    def create_vector_store(cls,
                            store_type: Optional[str] = None,
                            config: Optional[Dict[str, Any]] = None) -> BaseVectorStore:
        """
        创建向量数据库实例

        Args:
            store_type: 数据库类型，如果为 None 则从配置中读取
            config: 数据库配置，如果为 None 则从配置中读取

        Returns:
            BaseVectorStore: 向量数据库实例

        Raises:
            ValueError: 不支持的数据库类型
        """
        if config is None:
            config = VectorStoreConfig()

        if store_type is None:
            store_type = config.store_type

        if store_type not in cls._vector_stores:
            available_types = list(cls._vector_stores.keys())
            raise ValueError(f"Unsupported vector store type: {store_type}. Available types: {available_types}")

        store_class = cls._vector_stores[store_type]
        logger.debug(f"Creating vector store: {store_type}")
        return store_class(config)

    @classmethod
    def create_text_store(cls,
                          collection_name: str,
                          vector_size: int,
                          store_type: Optional[str] = None,
                          vector_store: Optional[BaseVectorStore] = None) -> BaseTextVectorStore:
        """
        创建文本向量存储实例

        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            store_type: 存储类型
            vector_store: 向量数据库实例，如果为 None 则创建新实例

        Returns:
            BaseTextVectorStore: 文本向量存储实例
        """
        if store_type is None:
            vs_config = VectorStoreConfig()
            store_type = vs_config.store_type

        if store_type not in cls._text_stores:
            available_types = list(cls._text_stores.keys())
            raise ValueError(f"Unsupported text store type: {store_type}. Available types: {available_types}")

        if vector_store is None:
            vector_store = cls.create_vector_store(store_type)

        store_class = cls._text_stores[store_type]
        logger.debug(f"Creating text store: {collection_name}")
        return store_class(vector_store, collection_name, vector_size)

    @classmethod
    def create_image_store(cls,
                           collection_name: str,
                           vector_size: int,
                           vector_key: str = "vector",
                           index_fields: Optional[list] = None,
                           store_type: Optional[str] = None,
                           vector_store: Optional[BaseVectorStore] = None) -> BaseImageVectorStore:
        """
        创建图像向量存储实例

        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            vector_key: 向量键名
            index_fields: 索引字段列表
            store_type: 存储类型
            vector_store: 向量数据库实例，如果为 None 则创建新实例

        Returns:
            BaseImageVectorStore: 图像向量存储实例
        """
        if store_type is None:
            vs_config = VectorStoreConfig()
            store_type = vs_config.store_type

        if store_type not in cls._image_stores:
            available_types = list(cls._image_stores.keys())
            raise ValueError(f"Unsupported image store type: {store_type}. Available types: {available_types}")

        if vector_store is None:
            vector_store = cls.create_vector_store(store_type)

        store_class = cls._image_stores[store_type]
        logger.debug(f"Creating image store: {collection_name}")
        return store_class(vector_store, collection_name, vector_key, vector_size, index_fields)
