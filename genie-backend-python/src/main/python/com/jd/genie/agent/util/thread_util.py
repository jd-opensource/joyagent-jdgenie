"""
Thread utility functions for concurrent operations.
线程工具类
"""
import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class ThreadUtil:
    """Utility class for thread operations."""
    
    _executor: Optional[ThreadPoolExecutor] = None
    _lock = threading.Lock()
    
    @staticmethod
    def init_pool(pool_size: int) -> None:
        """
        Initialize thread pool with specified size.
        初始化线程池
        """
        with ThreadUtil._lock:
            if ThreadUtil._executor is None:
                max_pool_size = max(pool_size, 1000)
                ThreadUtil._executor = ThreadPoolExecutor(
                    max_workers=max_pool_size,
                    thread_name_prefix="exe-pool"
                )
    
    @staticmethod
    def execute(runnable: Callable[[], None]) -> None:
        """
        Execute a runnable in the thread pool.
        在线程池中执行任务
        """
        if ThreadUtil._executor is None:
            ThreadUtil.init_pool(100)
        
        ThreadUtil._executor.submit(runnable)
    
    @staticmethod
    def get_countdown_latch(count: int) -> threading.Event:
        """
        Get a countdown latch equivalent (using Event).
        获取倒计时门闩等价物（使用Event）
        """
        # Python doesn't have CountDownLatch, use Event as simple alternative
        # For more complex scenarios, consider using threading.Barrier
        return threading.Event()
    
    @staticmethod
    def await_event(event: threading.Event) -> None:
        """
        Wait for event to be set.
        等待事件被设置
        """
        try:
            event.wait()
        except Exception as e:
            logger.warning(f"Event wait interrupted: {e}")
    
    @staticmethod
    def sleep(millis: int) -> None:
        """
        Sleep for specified milliseconds.
        休眠指定毫秒数
        """
        try:
            time.sleep(millis / 1000.0)
        except Exception as e:
            logger.warning(f"Sleep interrupted: {e}")
    
    @staticmethod
    def shutdown() -> None:
        """
        Shutdown the thread pool executor.
        关闭线程池执行器
        """
        with ThreadUtil._lock:
            if ThreadUtil._executor is not None:
                ThreadUtil._executor.shutdown(wait=True)
                ThreadUtil._executor = None


class AsyncCountdownLatch:
    """
    Async version of countdown latch for asyncio environments.
    异步版本的倒计时门闩
    """
    
    def __init__(self, count: int):
        self._count = count
        self._event = asyncio.Event()
        self._lock = asyncio.Lock()
    
    async def count_down(self) -> None:
        """Decrement the count."""
        async with self._lock:
            self._count -= 1
            if self._count <= 0:
                self._event.set()
    
    async def wait(self) -> None:
        """Wait until count reaches zero."""
        await self._event.wait()
    
    @property
    def count(self) -> int:
        """Get current count."""
        return self._count