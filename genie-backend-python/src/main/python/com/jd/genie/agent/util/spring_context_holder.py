"""
Spring context holder for Python - compatibility layer.
This provides a Spring-like dependency injection container for Python.
"""

from typing import Any, Dict, Optional
import threading


class ApplicationContext:
    """Simple application context for dependency injection."""
    
    def __init__(self):
        self._beans: Dict[str, Any] = {}
    
    def register_bean(self, name: str, bean: Any):
        """Register a bean in the context."""
        self._beans[name] = bean
    
    def get_bean(self, bean_type: Any) -> Any:
        """Get a bean by type."""
        # Try to find by class name
        type_name = bean_type.__name__ if hasattr(bean_type, '__name__') else str(bean_type)
        
        # Look for exact match first
        if type_name in self._beans:
            return self._beans[type_name]
        
        # Look for instance match
        for bean in self._beans.values():
            if isinstance(bean, bean_type):
                return bean
        
        # Return None if not found (Python style) instead of throwing exception
        return None


class SpringContextHolder:
    """
    Static holder for Spring-like application context.
    Provides compatibility with Java Spring patterns.
    """
    
    _context: Optional[ApplicationContext] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_application_context(cls) -> ApplicationContext:
        """Get the application context (singleton pattern)."""
        if cls._context is None:
            with cls._lock:
                if cls._context is None:
                    cls._context = ApplicationContext()
        return cls._context
    
    @classmethod
    def set_application_context(cls, context: ApplicationContext):
        """Set the application context."""
        with cls._lock:
            cls._context = context
    
    @classmethod
    def clear(cls):
        """Clear the context (for testing)."""
        with cls._lock:
            cls._context = None