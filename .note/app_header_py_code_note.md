# app/header.py Code Analysis

## File Summary

The `app/header.py` file implements the `HeaderEntity` class, which serves as a comprehensive HTTP header management system for the genie-client application. This class handles parsing, storing, and processing various HTTP request headers including cookies, timeout configurations, and custom server keys. It provides a clean abstraction layer for managing HTTP header data and extracting configuration parameters from incoming requests.

## Imports and Dependencies

```python
from starlette.datastructures import Headers
from typing import Optional
```

The file imports Starlette's Headers datastructure for HTTP header handling and Optional type for optional parameters.

## Class Definition

### `HeaderEntity`

**Class Purpose:**
Manages HTTP header information, focusing on cookie handling, timeout configuration, and custom server key processing. Acts as a data transfer object that extracts and stores relevant header information for use by SSE clients.

## Class Constants

### Timeout Configuration
- `DEFAULT_TIMEOUT = 5`: Default connection timeout in seconds
- `DEFAULT_SSE_READ_TIMEOUT = 60 * 5`: Default SSE read timeout (5 minutes)
- `MAX_TIMEOUT_MINUTES = 15`: Maximum allowed timeout in minutes
- `TIMEOUT_MULTIPLIER = 60`: Conversion factor from minutes to seconds

### Header Field Names
- `HEADER_COOKIE = "Cookie"`: Standard Cookie header field name
- `HEADER_TIMEOUT = "Timeout"`: Custom timeout header field name
- `HEADER_SERVER_KEYS = "X-Server-Keys"`: Custom server keys header field name

## Constructor

### `__init__()`

**Method Signature:**
```python
def __init__(self, headers: Optional[Headers] = None)
```

**Purpose:**
Initializes a new HeaderEntity instance with optional headers processing.

**Parameters:**
- `headers`: Optional Starlette Headers object containing HTTP request headers

**Key Logic:**
- Initializes instance variables with default values
- Sets up cookies, headers dictionary, and timeout configurations
- Calls `add_headers()` if headers are provided
- Ensures all instance variables have proper default values

**Instance Variables Initialized:**
- `cookies`: String containing cookie data (None by default)
- `headers`: Dictionary for custom header key-value pairs
- `timeout`: Connection timeout in seconds
- `sse_read_timeout`: SSE stream read timeout in seconds

## Public Methods

### `add_headers()`

**Method Signature:**
```python
def add_headers(self, headers: Headers) -> None
```

**Purpose:**
Processes and extracts relevant information from HTTP headers.

**Parameters:**
- `headers`: Starlette Headers object to process

**Key Logic:**
- Delegates to specialized private methods for different header types
- Calls `_extract_cookies()` for cookie processing
- Calls `_set_timeout_config()` for timeout configuration
- Calls `_process_server_keys()` for server key extraction
- Provides centralized header processing workflow

### `append_cookie()`

**Method Signature:**
```python
def append_cookie(self, cookie: str) -> None
```

**Purpose:**
Adds additional cookie data to existing cookies with proper formatting.

**Parameters:**
- `cookie`: Cookie string to append

**Key Logic:**
- Handles empty/null cookie strings gracefully
- If no existing cookies, sets the new cookie as the primary value
- If cookies exist, appends new cookie with "; " separator
- Maintains proper cookie format for HTTP headers

### `get_cookie_dict()`

**Method Signature:**
```python
def get_cookie_dict(self) -> dict[str, str]
```

**Purpose:**
Parses cookie string into a dictionary of key-value pairs.

**Return Value:**
- Dictionary with cookie names as keys and cookie values as values

**Key Logic:**
- Returns empty dictionary if no cookies exist
- Splits cookie string by semicolon separators
- Processes each cookie pair by splitting on "=" character
- Strips whitespace from keys and values
- Handles malformed cookies gracefully (skips entries without "=")

## Private Methods

### `_extract_cookies()`

**Method Signature:**
```python
def _extract_cookies(self, headers: Headers) -> None
```

**Purpose:**
Extracts cookie information from HTTP headers.

**Parameters:**
- `headers`: HTTP headers object

**Key Logic:**
- Retrieves Cookie header value using the configured header name
- Sets the cookies instance variable if cookie header exists
- Handles cases where Cookie header is absent

### `_set_timeout_config()`

**Method Signature:**
```python
def _set_timeout_config(self, headers: Headers) -> None
```

**Purpose:**
Configures timeout settings based on custom Timeout header.

**Parameters:**
- `headers`: HTTP headers object

**Key Logic:**
- Retrieves custom Timeout header value
- Parses timeout value as integer
- Sets connection timeout from header value
- Calculates SSE read timeout with maximum limit enforcement
- Caps SSE timeout at MAX_TIMEOUT_MINUTES for resource protection
- Provides error handling for invalid timeout values with warnings

**Timeout Calculation:**
- Uses minimum of provided timeout and MAX_TIMEOUT_MINUTES
- Multiplies minutes by TIMEOUT_MULTIPLIER (60) to get seconds
- Ensures reasonable resource limits while allowing customization

### `_process_server_keys()`

**Method Signature:**
```python
def _process_server_keys(self, headers: Headers) -> None
```

**Purpose:**
Extracts specific header values based on server key specifications.

**Parameters:**
- `headers`: HTTP headers object

**Key Logic:**
- Retrieves X-Server-Keys header containing comma-separated key list
- Splits server keys string by commas and trims whitespace
- Iterates through each specified key
- Looks up header values for each specified key
- Stores key-value pairs in the headers dictionary
- Skips empty keys and missing header values gracefully

**Server Keys Format:**
Expected format: "key1,key2,key3"
- Processes each key individually
- Extracts corresponding header values
- Builds custom headers dictionary for forwarding

## String Representation Methods

### `__str__()`

**Method Signature:**
```python
def __str__(self) -> str
```

**Purpose:**
Provides human-readable string representation of the HeaderEntity.

**Return Value:**
- Formatted string with key instance properties

**Format:**
```
HeaderEntity(cookies=<cookie_data>, timeout=<timeout>, sse_read_timeout=<sse_timeout>, headers_count=<count>)
```

### `__repr__()`

**Method Signature:**
```python
def __repr__(self) -> str
```

**Purpose:**
Provides detailed string representation for debugging purposes.

**Return Value:**
- Same format as `__str__()` for consistency

## Key Design Features

### Flexible Configuration
- Supports both default and custom timeout values
- Handles missing headers gracefully with fallback defaults
- Allows dynamic timeout configuration through HTTP headers

### Cookie Management
- Comprehensive cookie parsing and manipulation
- Support for multiple cookie formats
- Clean dictionary interface for cookie access

### Server Key Processing
- Dynamic header forwarding based on client specifications
- Flexible server key selection through comma-separated lists
- Safe handling of missing or invalid server keys

### Error Resilience
- Graceful handling of malformed headers
- Warning messages for configuration errors
- Fallback to default values when parsing fails

### Data Encapsulation
- Clean separation between raw headers and processed data
- Structured access to configuration parameters
- Type-safe interfaces for different data types

This class provides a robust foundation for HTTP header processing in the genie-client application, with particular focus on the unique requirements of MCP server communication.