# app/config.py Code Analysis

## File Summary

The `app/config.py` file defines configuration constants used throughout the genie-client application. It serves as a centralized configuration module containing default timeout values, header field names, and other constant values that control the behavior of the SSE client and HTTP request processing. The file provides a single source of truth for configuration parameters, making the application easier to maintain and configure.

## Configuration Categories

### Timeout Configuration Constants

#### `DEFAULT_TIMEOUT`
**Value:** `5`
**Type:** `int`
**Purpose:** Sets the default connection timeout in seconds for HTTP/SSE connections.
**Usage:** Used as fallback when no specific timeout is provided in requests.

#### `DEFAULT_SSE_READ_TIMEOUT`
**Value:** `60 * 5` (300 seconds / 5 minutes)
**Type:** `int`
**Purpose:** Defines the default timeout for reading SSE (Server-Sent Events) streams.
**Usage:** Applied when establishing long-lived SSE connections to prevent indefinite blocking.

#### `MAX_TIMEOUT_MINUTES`
**Value:** `15`
**Type:** `int`
**Purpose:** Sets the maximum allowed timeout duration in minutes to prevent excessively long timeouts.
**Usage:** Used to cap user-specified timeout values for resource protection.

#### `TIMEOUT_MULTIPLIER`
**Value:** `60`
**Type:** `int`
**Purpose:** Conversion factor to transform minutes into seconds for timeout calculations.
**Usage:** Applied when converting minute-based timeout specifications to seconds.

### HTTP Header Constants

#### `HEADER_COOKIE`
**Value:** `"Cookie"`
**Type:** `str`
**Purpose:** Standard HTTP header field name for cookie information.
**Usage:** Used to identify and extract cookie data from HTTP requests.

#### `HEADER_TIMEOUT`
**Value:** `"Timeout"`
**Type:** `str`
**Purpose:** Custom header field name for specifying timeout values in requests.
**Usage:** Allows clients to specify custom timeout values through HTTP headers.

#### `HEADER_SERVER_KEYS`
**Value:** `"X-Server-Keys"`
**Type:** `str`
**Purpose:** Custom header field name for specifying which server keys should be extracted.
**Usage:** Enables clients to request specific header fields to be forwarded to the server.

## Design Principles

### Centralized Configuration
- All configuration constants are defined in one location
- Provides consistency across the application
- Makes configuration changes easier to manage
- Reduces the risk of scattered hardcoded values

### Naming Conventions
- Uses uppercase naming for constants following Python conventions
- Descriptive names that clearly indicate purpose and usage
- Consistent prefixing for related constants (e.g., HEADER_* for header names)

### Type Consistency
- Integer values for numeric configurations
- String values for header names and identifiers
- Clear separation between different types of configuration

### Reasonable Defaults
- **Short Connection Timeout (5s)**: Provides quick feedback for connection issues
- **Longer SSE Timeout (5 minutes)**: Accommodates long-running operations
- **Maximum Timeout Limit (15 minutes)**: Prevents resource exhaustion
- **Standard Header Names**: Uses conventional HTTP header naming

## Usage Patterns

### Import Usage
These constants are typically imported and used throughout the application:
```python
from app.config import DEFAULT_TIMEOUT, HEADER_COOKIE
```

### Configuration Override
The constants serve as defaults that can be overridden by:
- Environment variables
- User-provided headers
- Runtime configuration

### Validation Boundaries
Constants like `MAX_TIMEOUT_MINUTES` provide boundaries for input validation, ensuring system stability and resource protection.

## Maintenance Considerations

### Single Source of Truth
- Changes to timeout values only need to be made in this file
- Reduces configuration drift across different parts of the application
- Makes it easier to tune performance parameters

### Documentation Value
- The constant names serve as documentation for their purpose
- Values are easily discoverable for developers
- Clear separation of concerns for different types of configuration

### Future Extensibility
The structure supports easy addition of new configuration constants while maintaining organization and consistency.