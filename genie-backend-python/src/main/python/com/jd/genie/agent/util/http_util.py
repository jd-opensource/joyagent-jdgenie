"""
HTTP utility functions using httpx instead of OkHttp.
HTTP工具类，使用httpx替代Java的OkHttp
"""
import asyncio
import logging
from typing import Any, Callable, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class SseEventListener:
    """SSE event listener interface."""
    
    def on_event(self, event: str) -> None:
        """Handle received SSE event."""
        pass
    
    def on_complete(self) -> None:
        """Handle request completion."""
        pass
    
    def on_error(self, error: Exception) -> None:
        """Handle request error."""
        pass


class HttpUtil:
    """HTTP utility class with timeout settings."""
    
    @staticmethod
    def _create_client(timeout_seconds: int) -> httpx.Client:
        """
        Create HTTP client with timeout settings.
        创建带有超时设置的HTTP客户端
        """
        timeout = httpx.Timeout(
            connect=timeout_seconds,
            read=timeout_seconds,
            write=timeout_seconds,
            pool=timeout_seconds
        )
        return httpx.Client(timeout=timeout)
    
    @staticmethod
    def post_json(url: str, json_params: str, headers: Optional[Dict[str, str]], timeout_seconds: int) -> Optional[str]:
        """
        Send POST request with JSON parameters.
        发送POST请求，以JSON格式传递参数
        
        Args:
            url: Request URL
            json_params: JSON format parameters
            headers: Optional request headers
            timeout_seconds: Timeout in seconds
            
        Returns:
            Response text if successful, None otherwise
        """
        try:
            client = HttpUtil._create_client(timeout_seconds)
            
            request_headers = {"Content-Type": "application/json"}
            if headers:
                request_headers.update(headers)
            
            with client:
                response = client.post(url, content=json_params, headers=request_headers)
                
                if response.is_success and response.content:
                    return response.text
                    
        except Exception as e:
            logger.error(f"HTTP POST request failed: {url}", exc_info=e)
        
        return None
    
    @staticmethod
    async def sse_request(
        url: str, 
        json_params: str, 
        headers: Optional[Dict[str, str]], 
        timeout_seconds: int, 
        event_listener: SseEventListener
    ) -> None:
        """
        Send SSE streaming request.
        发送SSE流式请求
        
        Args:
            url: Request URL
            json_params: JSON parameters
            headers: Optional request headers
            timeout_seconds: Timeout in seconds
            event_listener: Event listener for handling SSE events
        """
        try:
            timeout = httpx.Timeout(
                connect=timeout_seconds,
                read=timeout_seconds,
                write=timeout_seconds,
                pool=timeout_seconds
            )
            
            request_headers = {"Content-Type": "application/json"}
            if headers:
                request_headers.update(headers)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    content=json_params,
                    headers=request_headers
                ) as response:
                    
                    if response.is_success:
                        async for line in response.aiter_lines():
                            event_listener.on_event(line)
                        event_listener.on_complete()
                    else:
                        event_listener.on_error(Exception(f"SSE request failed with status code: {response.status_code}"))
                        
        except Exception as e:
            event_listener.on_error(e)
    
    @staticmethod
    def sse_request_sync(
        url: str,
        json_params: str,
        headers: Optional[Dict[str, str]],
        timeout_seconds: int,
        event_listener: SseEventListener
    ) -> None:
        """
        Synchronous wrapper for SSE request.
        SSE请求的同步包装器
        """
        asyncio.run(
            HttpUtil.sse_request(url, json_params, headers, timeout_seconds, event_listener)
        )