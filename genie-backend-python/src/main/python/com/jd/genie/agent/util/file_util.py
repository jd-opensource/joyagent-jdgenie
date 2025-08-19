"""
File utility functions.
文件工具类
"""
import logging
from typing import List, Optional

from ...dto.file import File

logger = logging.getLogger(__name__)


class FileUtil:
    """Utility class for file operations."""
    
    @staticmethod
    def format_file_info(files: List[File], filter_internal_file: bool) -> str:
        """
        Format file information into a string.
        格式化文件信息
        
        Args:
            files: List of files to format
            filter_internal_file: Whether to filter out internal files
            
        Returns:
            Formatted file information string
        """
        string_builder = []
        
        for file in files:
            if filter_internal_file and file.is_internal_file:
                # logger.info(f"filter file {file}")
                continue
            
            file_url = file.origin_oss_url if (file.origin_oss_url and file.origin_oss_url.strip()) else file.oss_url
            
            string_builder.append(
                f"fileName:{file.file_name} fileDesc:{file.description} fileUrl:{file_url}\n"
            )
        
        return "".join(string_builder)