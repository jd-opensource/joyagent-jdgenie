# app/logger.py Code Analysis

## File Summary

The `app/logger.py` file provides a comprehensive logging configuration system for the genie-client application. It implements flexible logging setup with support for console output, file rotation, environment-based configuration, and separate handling of different log levels. The module creates both runtime logs and error logs with automatic file rotation, making it suitable for production deployment. It emphasizes configurability through environment variables while providing sensible defaults.

## Imports and Dependencies

```python
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
```

Key dependencies include Python's standard logging system, OS environment handling, pathlib for modern path handling, and rotating file handlers for log management.

## Class Definition

### `LogConfig`

**Class Purpose:**
Centralizes all logging configuration parameters, reading from environment variables and providing defaults. Acts as a configuration data class that handles validation and parameter management for the logging system.

## LogConfig Constructor

### `__init__()`

**Method Signature:**
```python
def __init__(self):
```

**Purpose:**
Initializes logging configuration by reading environment variables and setting up default values.

**Configuration Categories:**

#### Basic Configuration
- `self.name`: Logger name from `LOGGER_NAME` environment variable
- `self.level`: Log level from `LOG_LEVEL` (default: "debug")

#### File Configuration
- `self.log_dir`: Log directory path from `LOG_DIR` (default: "Logs")
- `self.log_filename`: Runtime log filename from `RUNTIME_LOG_FILENAME` (default: "runtime.log")
- `self.error_log_filename`: Error log filename from `ERROR_LOG_FILENAME` (default: "error.log")

#### Rotation Configuration
- `self.max_bytes`: Maximum file size from `OG_MAX_BYTES` (default: 256MB)
- `self.backup_count`: Number of backup files from `LOG_BACKUP_COUNT` (default: 5)

#### Format Configuration
- `self.log_format`: Log message format with timestamp, name, level, file location, and message
- `self.date_format`: Date format from `LOG_DATE_FORMAT` (default: "%Y-%m-%d %H:%M:%S")

## LogConfig Methods

### `validate_level()`

**Method Signature:**
```python
def validate_level(self) -> int
```

**Purpose:**
Validates the configured log level and returns the appropriate logging constant.

**Return Value:**
- Integer representing the log level (from logging module constants)

**Key Logic:**
- Uses `getattr()` to retrieve logging level constant by name
- Falls back to `logging.INFO` for invalid level names
- Provides type-safe log level conversion

## Main Functions

### `setup_logger()`

**Function Signature:**
```python
def setup_logger(name: Optional[str] = None) -> logging.Logger
```

**Purpose:**
Creates and configures a complete logger instance with console and file handlers.

**Parameters:**
- `name`: Optional logger name (uses environment variable or default if None)

**Return Value:**
- Fully configured `logging.Logger` instance

**Key Logic:**
- Creates LogConfig instance for configuration management
- Determines logger name from parameter or configuration
- Retrieves existing logger or creates new one
- Prevents duplicate configuration by checking existing handlers
- Sets up log level with validation and warning for invalid levels
- Creates formatter with configured format and date format
- Adds console and file handlers through helper functions
- Logs successful initialization with logger name and level

**Exception Handling:**
- Raises `OSError` for file creation failures
- Raises `ValueError` for invalid configuration parameters

### `_add_console_handler()`

**Function Signature:**
```python
def _add_console_handler(logger: logging.Logger, formatter: logging.Formatter) -> None
```

**Purpose:**
Configures and adds console output handler to the logger.

**Parameters:**
- `logger`: Logger instance to configure
- `formatter`: Formatter to apply to console output

**Key Logic:**
- Creates StreamHandler for stdout output
- Applies the provided formatter
- Sets handler level to DEBUG (shows all messages)
- Adds handler to logger

**Design Choice:**
- Uses stdout instead of stderr for broader compatibility
- Sets DEBUG level to ensure all messages appear on console

### `_add_file_handlers()`

**Function Signature:**
```python
def _add_file_handlers(logger: logging.Logger, formatter: logging.Formatter, config: LogConfig) -> None
```

**Purpose:**
Creates and configures rotating file handlers for different log levels.

**Parameters:**
- `logger`: Logger instance to configure
- `formatter`: Formatter to apply to file output
- `config`: LogConfig instance with file configuration

**Key Logic:**
- Creates log directory structure with `mkdir(parents=True, exist_ok=True)`
- Sets up two separate file handlers:

#### Runtime Log Handler (INFO and below)
- Uses RotatingFileHandler for automatic file rotation
- Configured with max file size and backup count
- Sets UTF-8 encoding for international character support
- Uses custom filter to exclude WARNING and higher levels
- Captures DEBUG, INFO level messages

#### Error Log Handler (WARNING and above)
- Separate RotatingFileHandler for errors and warnings
- Same rotation configuration as runtime handler
- Sets level to WARNING to capture only serious issues
- Captures WARNING, ERROR, CRITICAL level messages

**Exception Handling:**
- Catches `OSError` during file handler creation
- Logs error and re-raises for proper error propagation
- Ensures directory creation failures are properly reported

### `get_logger()`

**Function Signature:**
```python
def get_logger(name: Optional[str] = None) -> logging.Logger
```

**Purpose:**
Convenience function that delegates to `setup_logger()`.

**Parameters:**
- `name`: Optional logger name

**Return Value:**
- Configured logger instance

**Key Logic:**
- Simple wrapper around `setup_logger()`
- Provides alternative function name for different usage patterns

## Module-Level Configuration

### Default Logger Instance

**Variable:** `default_logger`
**Creation:** `default_logger = setup_logger()`

**Purpose:**
Provides a pre-configured logger instance that can be imported and used immediately throughout the application.

**Usage Pattern:**
```python
from app.logger import default_logger as logger
logger.info("Message")
```

### Module Exports

**`__all__` Definition:**
```python
__all__ = ["setup_logger", "get_logger", "default_logger", "LogConfig"]
```

**Purpose:**
Explicitly defines the public API of the module, controlling what gets imported with `from app.logger import *`.

## Key Design Features

### Environment-Based Configuration
- All configuration parameters can be overridden via environment variables
- Provides flexibility for different deployment environments
- Supports Docker and cloud deployment patterns

### Dual File Logging Strategy
- Separates routine operations (runtime.log) from problems (error.log)
- Makes it easier to monitor application health
- Reduces noise when investigating issues

### Automatic File Rotation
- Prevents log files from growing indefinitely
- Configurable size limits and backup counts
- Maintains historical data while managing disk space

### UTF-8 Support
- Handles international characters in log messages
- Ensures proper encoding in file outputs
- Supports modern applications with diverse content

### Error Resilience
- Graceful handling of invalid configuration
- Fallback to sensible defaults
- Clear warning messages for configuration issues

### Production Ready
- Comprehensive error handling
- Configurable for different environments
- Proper resource management
- Detailed formatting for troubleshooting

### Logging Best Practices
- Separate handlers for different output destinations
- Appropriate log levels for different message types
- Structured log format with context information
- Avoids duplicate handler configuration

This logging system provides a robust foundation for monitoring and debugging the genie-client application in both development and production environments.