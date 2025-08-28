"""
Dependency container for Python equivalent of SpringContextHolder.
Python版本的Spring上下文持有者
"""
from typing import Any, Dict, Optional


class DependencyContainer:
    """Dependency container for managing application dependencies."""
    
    _config = None
    _beans: Dict[str, Any] = {}
    
    @classmethod
    def set_config(cls, config: Any) -> None:
        """Set the application configuration."""
        cls._config = config
    
    @classmethod
    def get_config(cls) -> Any:
        """Get the application configuration."""
        return cls._config
    
    @classmethod
    def register_bean(cls, name: str, bean: Any) -> None:
        """Register a bean in the container."""
        cls._beans[name] = bean
    
    @classmethod
    def get_bean(cls, name: str) -> Optional[Any]:
        """Get a bean from the container."""
        return cls._beans.get(name)
    
    @classmethod
    def has_bean(cls, name: str) -> bool:
        """Check if a bean exists in the container."""
        return name in cls._beans
    
    @classmethod
    def clear(cls) -> None:
        """Clear all beans and config."""
        cls._config = None
        cls._beans.clear()