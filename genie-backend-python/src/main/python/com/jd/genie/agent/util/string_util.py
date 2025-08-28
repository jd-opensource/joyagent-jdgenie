"""
String utility functions.
字符串工具类
"""
import random
import re
import string
import uuid
from typing import Dict, Optional, Set


class StringUtil:
    """Utility class for string operations."""
    
    CHAR_LOWER = "abcdefghijklmnopqrstuvwxyz"
    NUMBER = "0123456789"
    DATA_FOR_RANDOM_STRING = CHAR_LOWER + NUMBER
    
    @staticmethod
    def generate_random_string(length: int) -> str:
        """
        Generate a random string of specified length.
        生成指定长度的随机字符串
        """
        if length < 1:
            raise ValueError("Length must be positive")
        
        return ''.join(random.choices(StringUtil.DATA_FOR_RANDOM_STRING, k=length))
    
    @staticmethod
    def _luhn_bank_card_verify(card_number: str) -> bool:
        """
        Luhn algorithm for bank card verification.
        银行卡Luhn校验算法
        """
        total = 0
        alternate = False
        
        for i in range(len(card_number) - 1, -1, -1):
            digit = int(card_number[i])
            if alternate:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
            alternate = not alternate
            
        return total % 10 == 0
    
    @staticmethod
    def text_desensitization(content: str, sensitive_patterns_mapping: Dict[str, str]) -> str:
        """
        Desensitize sensitive information in text.
        文本脱敏处理
        """
        # Email desensitization
        email_pattern = re.compile(r'[a-zA-Z0-9\._%\+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}')
        for match in email_pattern.finditer(content):
            snippet = match.group()
            mask_idx = snippet.find("@")
            # Skip internal emails
            if "@jd.com" in content:
                continue
            content = content.replace(snippet, snippet[:mask_idx] + "＠" + snippet[mask_idx + 1:])
        
        # ID card desensitization
        id_pattern = re.compile(r'(?:[^\dA-Za-z_]|^)((?:[1-6][1-7]|50|71|81|82)\d{4}(?:19|20)\d{2}(?:0[1-9]|10|11|12)(?:[0-2][1-9]|10|20|30|31)\d{3}[0-9Xx])(?:[^\dA-Za-z_]|$)')
        for match in id_pattern.finditer(content):
            snippet = match.group(1)
            content = content.replace(snippet, snippet[:12] + "✿✿✿✿✿✿")
        
        # Phone number desensitization
        phone_pattern = re.compile(r'(?:[^\dA-Za-z_]|^)(1[3456789]\d{9})(?:[^\dA-Za-z_]|$)')
        for match in phone_pattern.finditer(content):
            snippet = match.group(1)
            content = content.replace(snippet, snippet[:3] + "✿✿✿✿" + snippet[7:])
        
        # Bank card desensitization
        bankcard_pattern = re.compile(r'(?:[^\dA-Za-z_]|^)(62(?:\d{14}|\d{17}))(?:[^\dA-Za-z_]|$)')
        for match in bankcard_pattern.finditer(content):
            snippet = match.group(1)
            if StringUtil._luhn_bank_card_verify(snippet):
                content = content.replace(snippet, snippet[:12] + "✿✿✿✿✿✿")
        
        # Password and other sensitive word desensitization
        for pattern, word_mapping in sensitive_patterns_mapping.items():
            try:
                start_index = pattern.find("^)") + 2
                end_index = pattern.rfind("[^")
                
                if start_index + 1 < end_index:
                    sensitive_word = pattern[start_index:end_index]
                    sensitive_pattern = re.compile(pattern)
                    
                    for match in sensitive_pattern.finditer(content):
                        snippet = match.group()
                        if content.startswith(sensitive_word):
                            content = content.replace(snippet, word_mapping + snippet[-1:])
                        else:
                            content = content.replace(snippet, snippet[0] + word_mapping + snippet[-1:])
                else:
                    content = content.replace(pattern, word_mapping)
            except Exception:
                # Fallback to simple replacement
                content = content.replace(pattern, word_mapping)
        
        return content
    
    @staticmethod
    def remove_special_chars(input_str: Optional[str]) -> str:
        """
        Remove special characters from string.
        移除字符串中的特殊字符
        """
        if not input_str:
            return ""
        
        special_chars = " \"&$@=;+?\\{^}%~[]<>#|'"
        special_chars_set: Set[str] = set(special_chars)
        
        result = []
        for char in input_str:
            if char not in special_chars_set:
                result.append(char)
        
        return ''.join(result)
    
    @staticmethod
    def get_uuid() -> str:
        """
        Generate a UUID string.
        生成UUID字符串
        """
        return str(uuid.uuid4())


# Test code (equivalent to Java main method)
if __name__ == "__main__":
    print(StringUtil.get_uuid())
    
    # Test special character removal
    # name = "123 $ 456 %%% ^ "
    # print(StringUtil.remove_special_chars(name))
    
    # name = None
    # print(">>" + StringUtil.remove_special_chars(name) + "<<")
    
    # Test desensitization
    # patterns = {
    #     "(?:[^A-Za-z0-9_-]|^)password[^A-Za-z0-9_-]": "PASSWORD",
    #     "(?:[^A-Za-z0-9_-]|^)asd[^A-Za-z0-9_-]": "ASD"
    # }
    
    # test_content = "asd 我的邮箱是test@example.com，身份证号是510104199001011234，手机号是13800138000，银行卡号是6226327514303272，哈哈password:::admin123 asd"
    # result = StringUtil.text_desensitization(test_content, patterns)
    # print(result)