"""
Chinese character detection utility.
中文字符检测工具类
"""
import time
import uuid
from typing import Optional


class ChineseCharacterCounter:
    """Utility class for Chinese character operations."""
    
    @staticmethod
    def is_chinese_character(ch: str) -> bool:
        """
        Check if a character is Chinese.
        检查字符是否为中文
        
        Args:
            ch: Character to check
            
        Returns:
            True if character is Chinese, False otherwise
        """
        if not ch:
            return False
        
        # Chinese character Unicode range: \u4E00 to \u9FA5
        return '\u4E00' <= ch <= '\u9FA5'
    
    @staticmethod
    def has_chinese_characters(text: Optional[str]) -> bool:
        """
        Check if text contains Chinese characters.
        检查文本是否包含中文字符
        
        Args:
            text: Text to check
            
        Returns:
            True if text contains Chinese characters, False otherwise
        """
        if not text:
            return False
        
        for char in text:
            if ChineseCharacterCounter.is_chinese_character(char):
                return True
        
        return False


# Test code (equivalent to Java main method)
if __name__ == "__main__":
    start = time.time()
    test_string = "贸正促销大发送咚咚噶十多个"
    has_chinese = ChineseCharacterCounter.has_chinese_characters(test_string)
    
    if has_chinese:
        print(str(uuid.uuid4()).replace("-", ""))
    
    print(f"字符串转换，耗时：{(time.time() - start) * 1000:.0f}ms")