# genie_tool/db/file_table.py Code Documentation

## File Summary

This module defines the database table model for file information storage using SQLModel (SQLAlchemy + Pydantic). It provides the schema for tracking uploaded files, their metadata, and storage locations within the Genie Tool system. The model combines SQLAlchemy ORM capabilities with Pydantic data validation.

## Table Model

### `FileInfo` Class
```python
class FileInfo(SQLModel, table=True)
```
- **Purpose**: Database table model for storing file metadata and tracking
- **Base Classes**: 
  - `SQLModel`: Combines SQLAlchemy and Pydantic functionality
  - `table=True`: Indicates this is a database table (not just a schema model)
- **Usage**: Represents files uploaded and managed by the system

## Table Schema

### Primary Key
```python
id: int | None = Field(default=None, primary_key=True)
```
- **Type**: Integer (auto-incrementing)
- **Purpose**: Unique identifier for each file record
- **Configuration**: 
  - Primary key constraint
  - Auto-generated (default=None allows SQLAlchemy to handle)
  - Optional type to handle creation vs retrieval scenarios

### File Identification
```python
file_id: str = Field(unique=True, nullable=True)
```
- **Type**: String
- **Purpose**: Business-level unique identifier for files
- **Configuration**: 
  - Unique constraint (no duplicate file_ids)
  - Nullable to allow flexibility in creation
- **Usage**: Generated from combination of request_id and filename

### File Metadata
```python
filename: str = Field()
file_path: str = Field()
description: Optional[str]
file_size: Optional[int]
```
- **filename**: Original name of the uploaded file
- **file_path**: Local filesystem path where file is stored
- **description**: Optional text description of file contents
- **file_size**: File size in bytes (optional, calculated during upload)

### Request Tracking
```python
request_id: Optional[str] = Field(default=None)
```
- **Type**: Optional string
- **Purpose**: Groups files by request/session
- **Usage**: Links files to specific API requests or user sessions
- **Default**: None (allows ungrouped files)

### Status Management
```python
status: int = Field(default=0)
```
- **Type**: Integer
- **Purpose**: Tracks file status/state
- **Default**: 0 (likely indicating initial/pending state)
- **Usage**: Could represent states like:
  - 0: Pending/Initial
  - 1: Active/Available  
  - -1: Deleted/Inactive

### Timestamp
```python
create_time: Optional[datetime] = Field(
    sa_type=DateTime, 
    default=None, 
    nullable=False,  
    sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
)
```
- **Type**: DateTime (optional in Python, required in database)
- **Purpose**: Records when the file record was created
- **Configuration**: 
  - `sa_type=DateTime`: Explicit SQLAlchemy column type
  - `default=None`: Python default (overridden by server default)
  - `nullable=False`: Database constraint (cannot be NULL)
  - `server_default=text("CURRENT_TIMESTAMP")`: Database sets timestamp automatically

## Technical Features

### SQLModel Integration
- **Dual Nature**: Works as both Pydantic model and SQLAlchemy table
- **Validation**: Pydantic validation for data integrity
- **ORM Capabilities**: Full SQLAlchemy relationship and query support
- **Type Hints**: Modern Python type annotations

### Database Constraints
- **Primary Key**: Automatic ID generation
- **Unique Constraint**: Prevents duplicate file_id values
- **Nullable Fields**: Flexible schema for optional data
- **Server Defaults**: Database-level timestamp generation

### Data Types
- **Modern Union Syntax**: Uses `int | None` instead of `Union[int, None]`
- **Optional Types**: Proper handling of nullable fields
- **DateTime Handling**: Explicit SQLAlchemy DateTime type configuration

## Usage Patterns

### Create New File Record
```python
file_info = FileInfo(
    file_id="unique_id_123",
    filename="document.pdf",
    file_path="/storage/files/document.pdf",
    description="Important document",
    file_size=1024000,
    request_id="req_456"
)
```

### Database Operations
```python
# Insert
session.add(file_info)
await session.commit()

# Query
result = await session.execute(select(FileInfo).where(FileInfo.file_id == "unique_id_123"))
file_info = result.scalars().first()
```

### Field Access (Pydantic Model)
```python
# Validation during creation
file_data = {
    "filename": "test.txt",
    "file_path": "/tmp/test.txt"
}
file_info = FileInfo(**file_data)  # Pydantic validation applied
```

## Key Design Decisions

### Flexible Nullability
- Many fields are optional to accommodate different file upload scenarios
- Allows partial records during multi-step upload processes

### Business vs Technical IDs
- `id`: Technical primary key for database efficiency
- `file_id`: Business identifier for application logic
- Separation allows for better data management

### Server-Side Timestamps
- Database generates timestamps for consistency
- Avoids client/server time synchronization issues
- Ensures accurate creation time recording

### Status Field Design
- Simple integer for extensible status system
- Allows for future status types without schema changes
- Efficient for database queries and indexing

## Integration Points

### File Storage System
- `file_path` field links to actual file system storage
- Enables file retrieval and validation operations

### Request Tracking
- `request_id` enables grouping files by user sessions
- Supports batch operations and cleanup processes

### Metadata Management  
- Description and size fields support rich file information
- Enables search and organization capabilities

### Audit Trail
- Creation timestamp provides audit capabilities
- Status field enables soft delete and lifecycle tracking