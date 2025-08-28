# genie_tool/api/tool.py Code Documentation

## File Summary

This module provides the main API endpoints for the Genie Tool's core functionality: code interpretation, report generation, and deep search. All endpoints support streaming responses and flexible output modes. The module handles file processing, integrates with AI agents, and manages real-time data streaming using Server-Sent Events (SSE).

## API Endpoints

### `POST /code_interpreter`
- **Function**: `post_code_interpreter(body: CIRequest)`
- **Purpose**: Executes code interpretation tasks using AI agent with optional file inputs
- **Parameters**: 
  - `body`: CIRequest containing task, file names, stream settings, and request metadata
- **Returns**: EventSourceResponse (streaming) or JSON response (non-streaming)
- **Key Logic**: 
  - Processes file URLs by prepending file server URL for relative paths
  - Creates async generator for streaming responses
  - Handles different stream modes: general, token-based, time-based
  - Yields different response types: CodeOutput, ActionOutput, or text chunks
  - Manages token accumulation and timing for controlled streaming
  - For non-streaming: collects all content and uploads as file

### `POST /report`
- **Function**: `post_report(body: ReportRequest)`
- **Purpose**: Generates reports in various formats (HTML, Markdown, PPT) from input files
- **Parameters**: 
  - `body`: ReportRequest extending CIRequest with file_type specification
- **Returns**: EventSourceResponse (streaming) or JSON response (non-streaming)
- **Key Logic**: 
  - Processes file URLs similar to code interpreter
  - Includes HTML content parser for PPT and HTML formats
  - Streams report generation with configurable modes
  - Uploads final report as file with appropriate file type handling
  - Converts PPT file type to HTML for compatibility

### `POST /deepsearch`
- **Function**: `post_deepsearch(body: DeepSearchRequest)`
- **Purpose**: Performs deep web search with AI-powered query processing and analysis
- **Parameters**: 
  - `body`: DeepSearchRequest with query, search engines, loop limits, and stream settings
- **Returns**: EventSourceResponse with search results and analysis
- **Key Logic**: 
  - Initializes DeepSearch with specified search engines
  - Creates streaming generator for real-time search updates
  - Supports configurable maximum search loops
  - Always returns streaming response (no non-streaming mode)

## Internal Helper Functions

### `_parser_html_content(content: str) -> str`
- **Purpose**: Cleans HTML content by removing markdown code block markers
- **Parameters**: 
  - `content`: Raw HTML content string
- **Returns**: Cleaned HTML content
- **Logic**: 
  - Removes ```html and ```\nhtml prefixes
  - Removes trailing ``` markers
  - Used in report generation for HTML and PPT formats

### `_stream()` (in code_interpreter)
- **Purpose**: Async generator for streaming code interpreter responses
- **Key Features**: 
  - Handles different chunk types (CodeOutput, ActionOutput, text)
  - Manages accumulation variables for token and time-based streaming
  - Processes stream modes with different trigger conditions
  - Ensures proper JSON formatting and final cleanup

### `_stream()` (in report)
- **Purpose**: Async generator for streaming report generation responses
- **Key Features**: 
  - Accumulates report content while streaming
  - Applies HTML content parsing for specific file types
  - Uploads final report file and includes in response
  - Maintains streaming state with proper completion signaling

### `_stream()` (in deepsearch)
- **Purpose**: Simple async generator wrapper for DeepSearch streaming
- **Key Features**: 
  - Passes through DeepSearch streaming results
  - Adds completion marker ("[DONE]")
  - Minimal processing overhead

## Streaming Modes

### General Mode
- Streams each chunk immediately as received
- No accumulation or batching
- Real-time character-by-character streaming

### Token Mode
- Accumulates tokens until threshold reached
- Streams in batches based on token count
- Configurable token threshold via `stream_mode.token`

### Time Mode  
- Accumulates content until time threshold reached
- Streams in batches based on elapsed time
- Configurable time threshold via `stream_mode.time`

## Response Types

### Code Interpreter Responses
- **CodeOutput**: Contains generated code and file information
- **ActionOutput**: Contains execution results with final flag
- **Text chunks**: Streaming content during processing

### Report Responses
- **Streaming content**: Progressive report generation
- **File information**: Metadata about generated report file
- **Final response**: Complete report with file links

### Deep Search Responses
- **Search results**: Query decomposition and document retrieval
- **Analysis**: AI-powered search result analysis
- **JSON formatted**: Structured response with metadata

## File Handling

### URL Processing
- Converts relative file paths to absolute URLs
- Prepends FILE_SERVER_URL environment variable
- Handles both HTTP URLs and local file paths
- Maintains file name integrity through URL encoding

### File Upload Integration
- Uses upload_file utility for content-based uploads
- Supports multiple file types (HTML, Markdown, Python, etc.)
- Generates file metadata and access URLs
- Manages file descriptions and size information

## Environment Integration

### Required Environment Variables
- `FILE_SERVER_URL`: Base URL for file server access
- Model-specific configurations passed through to underlying agents

### External Dependencies
- **DeepSearch**: For web search and analysis functionality  
- **report**: For document generation capabilities
- **code_interpreter_agent**: For AI-powered code execution
- **upload_file**: For file management and storage

## Technical Features

### Asynchronous Processing
- All endpoints use async/await patterns
- Stream processing with proper asyncio integration
- Concurrent file processing and AI model inference

### Error Handling
- Comprehensive exception management
- Proper cleanup for streaming connections
- Fallback handling for different response modes

### Performance Optimizations
- Streaming responses to reduce latency
- Configurable batching strategies
- Efficient file processing and upload mechanisms

## Security Considerations
- File path validation and URL sanitization
- Request ID tracking for audit trails
- Proper content type handling
- CORS support through middleware