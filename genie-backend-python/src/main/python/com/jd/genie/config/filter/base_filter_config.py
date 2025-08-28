"""
Base filter configuration for FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class BaseFilterConfig:
    """Configuration for base filters including CORS."""
    
    def __init__(self):
        """Initialize the filter configuration."""
        pass
    
    @staticmethod
    def configure_cors(app: FastAPI) -> None:
        """
        Configure CORS middleware for the FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all methods
            allow_headers=["*"],  # Allow all headers
        )
    
    @staticmethod
    def configure_filters(app: FastAPI) -> None:
        """
        Configure all filters for the FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        BaseFilterConfig.configure_cors(app)