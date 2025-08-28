#!/usr/bin/env python3
"""
Genie Backend Python Application

Main entry point for the Genie AI Agent backend service.
Equivalent to the Java GenieApplication.java Spring Boot application.
"""

import uvicorn
from fastapi import FastAPI
from src.main.python.com.jd.genie.config.genie_config import GenieConfig
from src.main.python.com.jd.genie.controller.genie_controller import GenieController


def create_app():
    """Application factory pattern for creating FastAPI app."""
    app = FastAPI(
        title="Genie Backend",
        description="Genie AI Agent backend service",
        version="0.0.1"
    )
    
    # Load configuration
    config = GenieConfig()
    
    # Register routers/controllers
    genie_controller = GenieController()
    app.include_router(genie_controller.router)
    
    return app


def main():
    """Main entry point - equivalent to Java's main method."""
    app = create_app()
    
    # Get configuration
    config = GenieConfig()
    server_config = config.get_server_config()
    
    # Start the application
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=server_config.get('port', 8080),
        reload=server_config.get('debug', False)
    )


if __name__ == '__main__':
    main()