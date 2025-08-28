# server.py Code Analysis

## File Summary

The `server.py` file is a FastAPI-based web server that provides a RESTful API for Model Context Protocol (MCP) server communication. It serves as a lightweight web service that acts as a client interface for MCP servers, providing endpoints for server connectivity testing, tool listing, and tool execution. The server handles HTTP requests and coordinates with MCP servers through SSE (Server-Sent Events) connections.

## Imports and Dependencies

The file imports several key modules:
- `datetime` for timestamp generation
- `FastAPI` framework components for web API functionality
- Custom application modules for SSE client functionality, header management, and logging

## FastAPI Application Instance

**Variable:** `app`

**Configuration:**
```python
app = FastAPI(
    title="Genie MCP Client API",
    version="0.1.0",
    description="A lightweight web service for Model Context Protocol (MCP) server communication",
    contact={"name": "Your Name/Team", "email": "your-email@example.com"},
    license_info={"name": "MIT"}
)
```

**Purpose:**
Creates the main FastAPI application instance with comprehensive metadata including title, version, description, contact information, and license details.

## API Endpoints

### `health_check()`

**Function Signature:**
```python
@app.get("/health")
async def health_check():
```

**Purpose:**
Provides a health check endpoint to verify that the API service is running and responsive.

**Parameters:**
- None

**Return Value:**
- Dictionary containing:
  - `status`: String indicating service health ("healthy")
  - `timestamp`: ISO format timestamp of the request
  - `version`: Current API version

**Key Logic:**
- Returns a simple health status response
- Includes current timestamp for monitoring purposes
- Provides version information for debugging

### `ping_server()`

**Function Signature:**
```python
@app.post("/v1/serv/pong")
async def ping_server(request: Request, server_url: str = Body(...))
```

**Purpose:**
Tests connectivity to a specified MCP server by sending a ping request.

**Parameters:**
- `request`: FastAPI Request object containing HTTP request details
- `server_url`: Target MCP server URL (required body parameter)

**Return Value:**
- Success response (200): Dictionary with success status and empty data
- Error response (500): Dictionary with error status and error message

**Key Logic:**
- Logs the incoming request with server URL and headers
- Creates an SseClient instance with the provided server URL and headers
- Attempts to ping the target server
- Returns appropriate success/error response based on ping result
- Handles exceptions and provides detailed error messages

### `list_tools()`

**Function Signature:**
```python
@app.post("/v1/tool/list")
async def list_tools(request: Request, server_url: str = Body(...))
```

**Purpose:**
Retrieves the list of available tools from a specified MCP server.

**Parameters:**
- `request`: FastAPI Request object containing HTTP request details
- `server_url`: Target MCP server URL (required body parameter)

**Return Value:**
- Success response (200): Dictionary with tool list in the data field
- Error response (500): Dictionary with error status and error message

**Key Logic:**
- Logs the incoming request details
- Creates SseClient instance with server URL and request headers
- Calls the MCP server to retrieve available tools
- Returns the tools list on success
- Provides comprehensive error handling and logging

### `call_tool()`

**Function Signature:**
```python
@app.post("/v1/tool/call")
async def call_tool(request: Request, server_url: str = Body(...), name: str = Body(...), arguments: dict = Body(...))
```

**Purpose:**
Executes a specific tool on the MCP server with provided arguments.

**Parameters:**
- `request`: FastAPI Request object containing HTTP request details
- `server_url`: Target MCP server URL (required body parameter)
- `name`: Name of the tool to execute (required body parameter)
- `arguments`: Dictionary of parameters to pass to the tool (required body parameter)

**Return Value:**
- Success response (200): Dictionary with tool execution results in the data field
- Error response (500): Dictionary with error status and detailed error message

**Key Logic:**
- Logs the tool call request with tool name and arguments
- Creates HeaderEntity from request headers
- Handles special Cookie parameter by appending it to the header entity
- Creates SseClient with server URL and configured headers
- Executes the specified tool with provided arguments
- Returns tool execution results
- Provides detailed error handling and logging for troubleshooting

## Application Startup

**Code Block:**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8188)
```

**Purpose:**
Starts the FastAPI server using Uvicorn ASGI server when the script is run directly.

**Configuration:**
- Host: "0.0.0.0" (accepts connections from any IP address)
- Port: 8188
- Uses the FastAPI app instance for handling requests

**Key Logic:**
- Only runs when script is executed directly (not imported)
- Starts the web server with the specified configuration
- Makes the API accessible on all network interfaces

## Error Handling Strategy

The application implements comprehensive error handling:
- All endpoints use try-catch blocks to handle exceptions
- Errors are logged with detailed information for debugging
- Consistent error response format across all endpoints
- HTTP status codes appropriately set (200 for success, 500 for errors)
- Error messages are descriptive and include context about the failed operation