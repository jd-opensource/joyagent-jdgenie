"""
生成模块

该模块负责最终答案的生成：
- 提示词管理
- 大模型调用
- 生成结果优化
"""

from .llm import LLMClient
from .prompt_manager import PromptManager

__all__ = ["PromptManager", "LLMClient"]
