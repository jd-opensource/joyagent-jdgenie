"""
SSE (Server-Sent Events) emitter with UTF-8 encoding for FastAPI.
支持UTF-8编码的SSE发射器，用于FastAPI
"""
from typing import Any, Dict, Optional
from fastapi.responses import StreamingResponse
import json


class SseEmitterUTF8:
    """
    SSE emitter with UTF-8 encoding.
    Python equivalent of Spring's SseEmitter with UTF-8 support.
    """
    
    def __init__(self, timeout: Optional[int] = None):
        """
        Initialize SSE emitter.
        
        Args:
            timeout: Timeout in milliseconds (None for no timeout)
        """
        self.timeout = timeout
        self._closed = False
        self._error_handlers = []
        self._timeout_handlers = []
        self._completion_handlers = []
    
    def on_error(self, handler) -> None:
        """Register error handler."""
        self._error_handlers.append(handler)
    
    def on_timeout(self, handler) -> None:
        """Register timeout handler."""
        self._timeout_handlers.append(handler)
    
    def on_completion(self, handler) -> None:
        """Register completion handler."""
        self._completion_handlers.append(handler)
    
    def send(self, data: Any, event: Optional[str] = None) -> None:
        """
        Send data through SSE.
        
        Args:
            data: Data to send
            event: Optional event name
        """
        if self._closed:
            return
        
        # This would be implemented in the actual streaming generator
        pass
    
    def complete(self) -> None:
        """Complete the SSE stream."""
        if not self._closed:
            self._closed = True
            for handler in self._completion_handlers:
                try:
                    handler()
                except Exception as e:
                    print(f"Error in completion handler: {e}")
    
    def complete_with_error(self, error: Exception) -> None:
        """Complete the SSE stream with error."""
        if not self._closed:
            self._closed = True
            for handler in self._error_handlers:
                try:
                    handler(error)
                except Exception as e:
                    print(f"Error in error handler: {e}")
    
    def to_streaming_response(self, generator):
        """
        Convert to FastAPI StreamingResponse with proper headers.
        转换为FastAPI StreamingResponse，包含正确的头部信息
        """
        headers = {
            "Content-Type": "text/event-stream; charset=utf-8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
        
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers=headers
        )


def format_sse_data(data: Any, event: Optional[str] = None, id_value: Optional[str] = None) -> str:
    """
    Format data for SSE transmission.
    格式化SSE传输数据
    
    Args:
        data: Data to format
        event: Optional event name
        id_value: Optional event ID
        
    Returns:
        Formatted SSE string
    """
    lines = []
    
    if id_value:
        lines.append(f"id: {id_value}")
    
    if event:
        lines.append(f"event: {event}")
    
    if isinstance(data, (dict, list)):
        data_str = json.dumps(data, ensure_ascii=False)
    else:
        data_str = str(data)
    
    # Split data into multiple lines if needed
    for line in data_str.split('\n'):
        lines.append(f"data: {line}")
    
    lines.append("")  # Empty line to end the event
    
    return "\n".join(lines)