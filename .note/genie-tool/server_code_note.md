# server.py Code Documentation

## File Summary

This is the main FastAPI application entry point for the Genie Tool server. It sets up the web application, configures middleware, registers API routes, and provides a command-line interface for starting the server. The server provides API endpoints for code interpretation, report generation, file management, and deep search functionality.

## Functions and Methods

### `print_logo()`
- **Purpose**: Displays ASCII art logo for "Genie Tool" using pyfiglet
- **Parameters**: None
- **Returns**: None (prints to console)
- **Logic**: Uses the "slant" font to render the application name as ASCII art

### `log_setting()`
- **Purpose**: Configures logging for the application using loguru
- **Parameters**: None
- **Returns**: None
- **Logic**: 
  - Gets log path from environment variable `LOG_PATH` or defaults to `logs/server.log`
  - Sets log format with timestamp, level, module, function, and message
  - Configures log rotation at 200 MB

### `create_app()` -> FastAPI
- **Purpose**: Creates and configures the main FastAPI application instance
- **Parameters**: None
- **Returns**: Configured FastAPI application object
- **Logic**: 
  - Creates FastAPI app with startup events (logging and logo display)
  - Registers middleware and routes
  - Returns the configured app

### `register_middleware(app: FastAPI)`
- **Purpose**: Registers middleware components for the FastAPI application
- **Parameters**: 
  - `app`: FastAPI application instance
- **Returns**: None
- **Logic**: 
  - Adds UnknownException middleware for error handling
  - Configures CORS middleware with permissive settings (allows all origins, methods, headers)
  - Adds HTTPProcessTimeMiddleware for request timing

### `register_router(app: FastAPI)`
- **Purpose**: Registers API route handlers with the FastAPI application
- **Parameters**: 
  - `app`: FastAPI application instance  
- **Returns**: None
- **Logic**: Imports and includes the main API router from `genie_tool.api`

## Main Execution Block

### Command Line Interface
- **Purpose**: Provides command-line interface for starting the server
- **Parameters**: 
  - `--host`: Server host address (default: "0.0.0.0")
  - `--port`: Server port number (default: 1601)
  - `--workers`: Number of worker processes (default: 10)
- **Logic**: 
  - Uses OptionParser to parse command line arguments
  - Runs uvicorn server with specified configuration
  - Enables reload mode when `ENV=local` environment variable is set

## Key Components

### Dependencies
- **FastAPI**: Web framework for building APIs
- **uvicorn**: ASGI server for running the application
- **loguru**: Advanced logging library
- **dotenv**: Environment variable loading
- **pyfiglet**: ASCII art text generation
- **starlette**: CORS middleware

### Environment Variables
- `LOG_PATH`: Custom log file location
- `ENV`: Environment mode (enables reload when set to "local")

### Application Structure
- Follows FastAPI best practices with separate middleware and router configuration
- Implements proper logging and error handling
- Uses startup events for initialization tasks
- Supports both development and production configurations

## Usage

The server can be started with default settings:
```bash
python server.py
```

Or with custom configuration:
```bash
python server.py --host 127.0.0.1 --port 8080 --workers 5
```

The application serves as the main entry point for the Genie Tool system, which provides AI-powered code interpretation, report generation, and search capabilities.