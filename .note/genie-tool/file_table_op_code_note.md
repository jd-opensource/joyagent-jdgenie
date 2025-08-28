# genie_tool/db/file_table_op.py Code Documentation

## File Summary

This module provides database operations and file storage management for the Genie Tool system. It includes a file database abstraction layer for local file storage and a comprehensive set of operations for managing file metadata in the database. The module handles both file system storage and database record management with proper async support.

## File Database System

### `_FileDB` Class
- **Purpose**: Handles local file system storage operations
- **Initialization**: Sets up working directory from environment or defaults
- **Directory Management**: Automatically creates required directories

#### Constructor
```python
def __init__(self):
    self._work_dir = os.getenv("FILE_SAVE_PATH", "file_db_dir")
    if not os.path.exists(self._work_dir):
        os.makedirs(self._work_dir)
```
- **Working Directory**: Configurable via `FILE_SAVE_PATH` environment variable
- **Default Location**: "file_db_dir" in current working directory  
- **Auto-creation**: Creates directory if it doesn't exist

#### `save(file_name, content, scope) -> str`
- **Purpose**: Saves string content to a file within a scoped directory
- **Parameters**: 
  - `file_name`: Name of file to create (auto-adds .txt extension if no extension)
  - `content`: String content to write
  - `scope`: Directory scope (typically request_id for organization)
- **Returns**: Full file path of saved file
- **Logic**: 
  - Normalizes filename using basename for security
  - Adds .txt extension for files without extensions
  - Creates scoped subdirectory if needed
  - Writes content as text file

#### `save_by_data(file: UploadFile) -> str`
- **Purpose**: Saves binary file data from FastAPI UploadFile
- **Parameters**: 
  - `file`: FastAPI UploadFile object with filename and binary data
- **Returns**: Full path to saved file
- **Logic**: 
  - Extracts filename and binary data from UploadFile
  - Saves directly to working directory (no scoping)
  - Writes binary data using "wb" mode

### FileDB Singleton
```python
FileDB = _FileDB()
```
- **Purpose**: Global singleton instance for file database operations
- **Usage**: Provides centralized file storage access across the application

## File Operations Class

### `FileInfoOp` Class
- **Purpose**: Provides static methods for database operations on FileInfo records
- **Pattern**: Uses class-based organization for related database operations
- **Timing**: All methods are decorated with `@timer()` for performance monitoring

#### `add_by_content(filename, content, file_id, description, request_id) -> FileInfo`
- **Purpose**: Creates file record from string content
- **Parameters**: 
  - `filename`: Original filename
  - `content`: File content as string
  - `file_id`: Unique identifier for the file
  - `description`: Optional description (default: None)
  - `request_id`: Request/session identifier (default: None)
- **Returns**: Created or updated FileInfo object
- **Logic**: 
  - Uses FileDB to save content to filesystem
  - Calculates file size from saved file
  - Creates FileInfo with metadata
  - Calls `add()` method to persist to database

#### `add_by_file(file, file_id, request_id) -> FileInfo`
- **Purpose**: Creates file record from UploadFile object
- **Parameters**: 
  - `file`: FastAPI UploadFile object
  - `file_id`: Unique identifier for the file
  - `request_id`: Request/session identifier (default: None)
- **Returns**: Created or updated FileInfo object
- **Logic**: 
  - Uses FileDB to save file data to filesystem
  - Extracts filename from UploadFile
  - Sets empty description
  - Calculates file size and creates FileInfo record

#### `add(file_info: FileInfo) -> FileInfo`
- **Purpose**: Inserts or updates FileInfo record in database
- **Parameters**: 
  - `file_info`: FileInfo object to persist
- **Returns**: Final FileInfo object from database
- **Logic**: 
  - Checks if file_id already exists in database
  - If exists: Updates status and file_size of existing record
  - If new: Inserts new record
  - Commits transaction and returns fresh database object

#### `get_by_file_id(file_id: str) -> FileInfo`
- **Purpose**: Retrieves single FileInfo by file_id
- **Parameters**: 
  - `file_id`: Unique file identifier
- **Returns**: FileInfo object or None if not found
- **Logic**: 
  - Uses SQLModel select query with WHERE clause
  - Returns first matching record or None

#### `get_by_file_ids(file_ids: List[str]) -> List[FileInfo]`
- **Purpose**: Retrieves multiple FileInfo records by file_ids
- **Parameters**: 
  - `file_ids`: List of file identifiers
- **Returns**: List of matching FileInfo objects
- **Logic**: 
  - Uses SQL IN clause for efficient batch retrieval
  - Returns all matching records

#### `get_by_request_id(request_id: str) -> List[FileInfo]`
- **Purpose**: Retrieves all files associated with a request/session
- **Parameters**: 
  - `request_id`: Request or session identifier
- **Returns**: List of FileInfo objects for the request
- **Logic**: 
  - Filters by request_id field
  - Returns all files in the request/session

## URL Generation Functions

### `get_file_preview_url(file_id: str, file_name: str) -> str`
- **Purpose**: Generates URL for file preview endpoint
- **Parameters**: 
  - `file_id`: File identifier (actually request_id in current implementation)
  - `file_name`: Name of the file
- **Returns**: Complete preview URL
- **Format**: `{FILE_SERVER_URL}/preview/{file_id}/{file_name}`

### `get_file_download_url(file_id: str, file_name: str) -> str`
- **Purpose**: Generates URL for file download endpoint  
- **Parameters**: 
  - `file_id`: File identifier (actually request_id in current implementation)
  - `file_name`: Name of the file
- **Returns**: Complete download URL
- **Format**: `{FILE_SERVER_URL}/download/{file_id}/{file_name}`

## Technical Features

### Environment Configuration
- **FILE_SAVE_PATH**: Configures local file storage directory
- **FILE_SERVER_URL**: Base URL for file server endpoints

### Async Database Operations
- All database methods use async/await patterns
- Proper session management with context managers
- Automatic session cleanup and error handling

### File Storage Strategy
- **Scoped Storage**: Files organized by request_id for isolation
- **Security**: Uses basename() to prevent path traversal
- **Flexibility**: Supports both content and binary file uploads
- **Auto-extension**: Adds .txt extension for plain content files

### Database Patterns
- **Upsert Logic**: Updates existing records instead of creating duplicates
- **Batch Operations**: Efficient multi-record queries
- **Status Management**: Maintains file status for lifecycle tracking

### Performance Optimizations
- **Timer Decorators**: Performance monitoring on all operations
- **Efficient Queries**: Uses appropriate SQL patterns (IN clause, indexed lookups)
- **Connection Management**: Proper async session handling

## Error Handling and Edge Cases

### File System Operations
- Directory creation with proper error handling
- Binary vs text file handling
- Path normalization for security

### Database Operations
- Handles existing vs new records gracefully
- Proper transaction management
- None handling for optional fields

### URL Generation
- Environment variable dependency for base URLs
- Consistent URL formatting across functions

## Integration Points

### FastAPI Integration
- Compatible with FastAPI UploadFile objects
- Supports async route handlers
- Provides URL generation for API responses

### File System Integration
- Local file storage with configurable location
- Organized directory structure by request
- Support for different file types and content

### Database Integration
- Full SQLModel/SQLAlchemy ORM integration
- Transaction management
- Efficient querying patterns