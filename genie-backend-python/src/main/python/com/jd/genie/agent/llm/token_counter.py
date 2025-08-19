"""
Token counter class for calculating token usage
"""
import logging
import math
from typing import List, Dict, Any, Union

logger = logging.getLogger(__name__)


class TokenCounter:
    """
    Token counter class for calculating token usage in messages and content
    """
    
    # Token constants
    BASE_MESSAGE_TOKENS = 4
    FORMAT_TOKENS = 2
    LOW_DETAIL_IMAGE_TOKENS = 85
    HIGH_DETAIL_TILE_TOKENS = 170
    
    # Image processing constants
    MAX_SIZE = 2048
    HIGH_DETAIL_TARGET_SHORT_SIDE = 768
    TILE_SIZE = 512
    
    def __init__(self):
        """Initialize the token counter"""
        pass
    
    def count_text(self, text: str) -> int:
        """
        Calculate the token count for text
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Number of tokens (simplified as character count)
        """
        return len(text) if text else 0
    
    def count_image(self, image_item: Dict[str, Any]) -> int:
        """
        Calculate the token count for an image
        
        Args:
            image_item: Dictionary containing image information
            
        Returns:
            Number of tokens for the image
        """
        detail = image_item.get("detail", "medium")
        
        # Low detail level returns fixed 85 tokens
        if detail == "low":
            return self.LOW_DETAIL_IMAGE_TOKENS
        
        # High detail level calculated based on dimensions
        if detail in ["high", "medium"]:
            if "dimensions" in image_item:
                dimensions = image_item["dimensions"]
                return self._calculate_high_detail_tokens(dimensions[0], dimensions[1])
        
        # Default values
        if detail == "high":
            return self._calculate_high_detail_tokens(1024, 1024)  # 765 tokens
        elif detail == "medium":
            return 1024
        else:
            return 1024  # Default to medium size
    
    def _calculate_high_detail_tokens(self, width: int, height: int) -> int:
        """
        Calculate token count for high detail images
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
            
        Returns:
            Number of tokens for the high detail image
        """
        # Step 1: Scale to fit within MAX_SIZE x MAX_SIZE square
        if width > self.MAX_SIZE or height > self.MAX_SIZE:
            scale = self.MAX_SIZE / max(width, height)
            width = int(width * scale)
            height = int(height * scale)
        
        # Step 2: Scale shortest side to HIGH_DETAIL_TARGET_SHORT_SIDE
        scale = self.HIGH_DETAIL_TARGET_SHORT_SIDE / min(width, height)
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        
        # Step 3: Calculate number of 512px tiles
        tiles_x = math.ceil(scaled_width / self.TILE_SIZE)
        tiles_y = math.ceil(scaled_height / self.TILE_SIZE)
        total_tiles = tiles_x * tiles_y
        
        # Step 4: Calculate final token count
        return (total_tiles * self.HIGH_DETAIL_TILE_TOKENS) + self.LOW_DETAIL_IMAGE_TOKENS
    
    def count_content(self, content: Any) -> int:
        """
        Calculate token count for message content
        
        Args:
            content: Content to count tokens for (string, list, etc.)
            
        Returns:
            Number of tokens in the content
        """
        if content is None:
            return 0
        
        if isinstance(content, str):
            return self.count_text(content)
        
        if isinstance(content, list):
            token_count = 0
            for item in content:
                if isinstance(item, str):
                    token_count += self.count_text(item)
                elif isinstance(item, dict):
                    if "text" in item:
                        token_count += self.count_text(item["text"])
                    elif "image_url" in item:
                        token_count += self.count_image(item["image_url"])
            return token_count
        
        return 0
    
    def count_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> int:
        """
        Calculate token count for tool calls
        
        Args:
            tool_calls: List of tool call dictionaries
            
        Returns:
            Number of tokens in the tool calls
        """
        token_count = 0
        for tool_call in tool_calls:
            if "function" in tool_call:
                function = tool_call["function"]
                token_count += self.count_text(function.get("name", ""))
                token_count += self.count_text(function.get("arguments", ""))
        return token_count
    
    def count_message_tokens(self, message: Dict[str, Any]) -> int:
        """
        Calculate token count for a single message
        
        Args:
            message: Message dictionary
            
        Returns:
            Number of tokens in the message
        """
        tokens = self.BASE_MESSAGE_TOKENS  # Base tokens per message
        
        # Add role tokens
        tokens += self.count_text(str(message.get("role", "")))
        
        # Add content tokens
        if "content" in message:
            tokens += self.count_content(message["content"])
        
        # Add tool call tokens
        if "tool_calls" in message:
            tokens += self.count_tool_calls(message["tool_calls"])
        
        # Add name and tool call ID tokens
        tokens += self.count_text(message.get("name", ""))
        tokens += self.count_text(message.get("tool_call_id", ""))
        
        return tokens
    
    def count_list_message_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Calculate total token count for a list of messages
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Total number of tokens in all messages
        """
        total_tokens = self.FORMAT_TOKENS  # Base format tokens
        for message in messages:
            total_tokens += self.count_message_tokens(message)
        return total_tokens