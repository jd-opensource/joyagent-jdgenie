#!/usr/bin/env python3
"""
Genie Backend Python Application

Main entry point for the Genie AI Agent backend service.
Equivalent to the Java GenieApplication.java Spring Boot application.
"""

import os
import sys
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the src/main/python directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from com.jd.genie.config.genie_config import GenieConfig
from com.jd.genie.controller.genie_controller import router as genie_router
from com.jd.genie.service.impl.agent_handler_factory import AgentHandlerFactory
from com.jd.genie.service.impl.gpt_process_service_impl import GptProcessServiceImpl
from com.jd.genie.service.impl.multi_agent_service_impl import MultiAgentServiceImpl
from com.jd.genie.service.impl.plan_solve_handler_impl import PlanSolveHandlerImpl
from com.jd.genie.service.impl.react_handler_impl import ReactHandlerImpl
from com.jd.genie.agent.util.spring_context_holder import SpringContextHolder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_app():
    """Application factory pattern for creating FastAPI app."""
    app = FastAPI(
        title="Genie Backend",
        description="Genie AI Agent backend service",
        version="0.0.1"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Load configuration
    config = GenieConfig()
    
    # Initialize Spring context holder for Java compatibility
    context = SpringContextHolder.get_application_context()
    context.register_bean('GenieConfig', config)
    
    # Initialize handlers first
    handlers = [
        PlanSolveHandlerImpl(config),
        ReactHandlerImpl(config)
    ]
    
    # Create agent handler factory with registered handlers
    agent_handler_factory = AgentHandlerFactory(handlers)
    
    # Initialize services (dependency injection)
    gpt_process_service = GptProcessServiceImpl(config)
    # Create handler map for multi-agent service
    handler_map = {}  # Will be populated as needed
    multi_agent_service = MultiAgentServiceImpl(config, handler_map)
    
    # Register services in Spring context
    context.register_bean('GptProcessServiceImpl', gpt_process_service)
    context.register_bean('MultiAgentServiceImpl', multi_agent_service)
    context.register_bean('AgentHandlerFactory', agent_handler_factory)
    
    # Store services in app state for dependency injection
    app.state.config = config
    app.state.gpt_process_service = gpt_process_service
    app.state.multi_agent_service = multi_agent_service
    app.state.agent_handler_factory = agent_handler_factory
    
    # Register routers/controllers
    app.include_router(genie_router)
    
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