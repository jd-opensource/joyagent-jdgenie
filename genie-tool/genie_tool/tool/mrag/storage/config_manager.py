"""
向量存储配置管理模块

提供集中化的配置管理，避免重复读取配置文件。
"""
import os
from typing import Dict, Optional

import dotenv

dotenv.load_dotenv()


class VectorStoreConfig:
    """向量存储配置管理类"""

    def __init__(self, config_dict: Optional[Dict] = None):
        """
        初始化配置
        
        Args:
            config_dict: 配置字典，如果为 None 则从配置文件读取
        """
        self.store_type = os.getenv("VECTOR_STORE_TYPE")
        self.text_collection = os.getenv("TEXT_COLLECTION")
        self.image_collection = os.getenv("IMAGE_COLLECTION")
        self.page_collection = os.getenv("PAGE_COLLECTION")
        self.text_dimension = int(os.getenv("TEXT_EMBEDDING_DIMENSION"))
        self.image_dimension = int(os.getenv("IMAGE_EMBEDDING_DIMENSION"))

    @property
    def page_dimension(self) -> int:
        """页面向量维度"""
        return self.image_dimension
