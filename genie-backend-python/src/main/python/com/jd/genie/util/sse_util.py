"""
SSE utility functions for building and managing SSE connections.
SSE工具类，用于构建和管理SSE连接
"""
import logging
from typing import Optional, Callable, Any

from .sse_emitter_utf8 import SseEmitterUTF8

logger = logging.getLogger(__name__)


class SseUtil:
    """Utility class for SSE operations."""
    
    @staticmethod
    def build(timeout: Optional[int], request_id: str) -> SseEmitterUTF8:
        """
        Build an SSE emitter with error, timeout and completion handlers.
        构建带有错误、超时和完成处理器的SSE发射器
        
        Args:
            timeout: Timeout in milliseconds
            request_id: Request ID for logging
            
        Returns:
            Configured SSE emitter
        """
        sse_emitter = SseEmitterUTF8(timeout)
        
        # Error handler
        def on_error(error: Exception) -> None:
            logger.error(f"SseSession Error, msg: {str(error)}, requestId: {request_id}")
            sse_emitter.complete_with_error(error)
        
        # Timeout handler
        def on_timeout() -> None:
            logger.info(f"SseSession Timeout, requestId: {request_id}")
            sse_emitter.complete()
        
        # Completion handler
        def on_completion() -> None:
            logger.info(f"SseSession Completion, requestId: {request_id}")
        
        sse_emitter.on_error(on_error)
        sse_emitter.on_timeout(on_timeout)
        sse_emitter.on_completion(on_completion)
        
        return sse_emitter
    
    @staticmethod
    def create_sse_generator(data_generator: Callable[[], Any], sse_emitter: SseEmitterUTF8):
        """
        Create an SSE generator function for FastAPI StreamingResponse.
        为FastAPI StreamingResponse创建SSE生成器函数
        
        Args:
            data_generator: Function that yields data to send
            sse_emitter: SSE emitter instance
        """
        try:
            for data in data_generator():
                if sse_emitter._closed:
                    break
                
                # Format and yield SSE data
                from .sse_emitter_utf8 import format_sse_data
                sse_data = format_sse_data(data)
                yield sse_data
                
        except Exception as e:
            logger.error(f"Error in SSE generator: {e}")
            sse_emitter.complete_with_error(e)
            # Send error message to client
            error_data = format_sse_data({"error": str(e)}, event="error")
            yield error_data
        finally:
            if not sse_emitter._closed:
                sse_emitter.complete()
            # Send final close message
            yield "data: [DONE]\n\n"