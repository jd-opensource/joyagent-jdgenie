# genie_tool/model/protocal.py Code Documentation

## File Summary

Defines Pydantic models for API request/response schemas including streaming modes, file operations, and tool requests. Provides data validation and serialization for all API endpoints.

## Key Classes

### `StreamMode`
- **Purpose**: Configures streaming response behavior
- **Fields**: mode (general/token/time), token count, time interval
- **Usage**: Controls how responses are batched and delivered

### `CIRequest` (Code Interpreter Request)
- **Purpose**: Request model for code interpretation tasks
- **Key Fields**: 
  - `task`: Description of code task to perform
  - `file_names`: List of input files for processing
  - `stream_mode`: Streaming configuration
  - `request_id`: Unique request identifier
- **Features**: Supports alias mapping for camelCase API compatibility

### `ReportRequest`
- **Purpose**: Extends CIRequest for report generation
- **Additional Field**: `file_type` (html/markdown/ppt)
- **Usage**: Specifies output format for generated reports

### `FileRequest` & `FileUploadRequest`
- **Purpose**: File operation request models
- **Features**: 
  - Computed file_id property using MD5 hash
  - Support for content-based and metadata uploads
  - Request/filename combination for unique identification

### `DeepSearchRequest`
- **Purpose**: Deep search functionality configuration
- **Key Features**: 
  - Multiple search engine support (bing, jina, sogou)
  - Configurable max search loops
  - Stream mode support

## Utility Functions

### `get_file_id(request_id, file_name) -> str`
- **Purpose**: Generates unique file identifier
- **Algorithm**: MD5 hash of request_id + file_name
- **Usage**: Consistent file identification across system

## Key Design Patterns

- **Alias Support**: Uses `Field(alias=...)` for API compatibility
- **Validation**: Pydantic automatic validation and type checking
- **Computed Properties**: Dynamic field generation
- **Default Values**: Sensible defaults for optional parameters
- **Type Safety**: Literal types for constrained values