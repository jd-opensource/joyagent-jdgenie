# genie_tool/model/file_info.py Code Documentation

## File Summary

This module provides an alternative SQLAlchemy-based file information model using modern SQLAlchemy 2.0+ patterns. It defines database table structures for file metadata storage with advanced features like declarative base classes, mapped columns, and automatic table naming. This appears to be a more advanced version compared to the SQLModel-based file_table.py.

## Base Classes

### `MappedBase` Class
```python
class MappedBase(AsyncAttrs, DeclarativeBase):
```
- **Purpose**: Base class for all database models using modern SQLAlchemy patterns
- **Inheritance**: 
  - `AsyncAttrs`: Enables async attribute loading and relationships
  - `DeclarativeBase`: Modern SQLAlchemy 2.0+ declarative base
- **Features**: Provides foundation for async ORM operations and advanced mapping

#### Automatic Table Naming
```python
@declared_attr.directive
def __tablename__(cls) -> str:
    return cls.__name__.lower()
```
- **Purpose**: Automatically generates table names from class names
- **Logic**: Converts class name to lowercase for table name
- **Example**: `FileInfo` class → `fileinfo` table

### `DataClassBase` Class
```python
class DataClassBase(MappedAsDataclass, MappedBase):
    """声明性数据类基类"""
    __abstract__ = True
```
- **Purpose**: Base class combining dataclass features with SQLAlchemy mapping
- **Inheritance**: 
  - `MappedAsDataclass`: Integrates Python dataclass functionality
  - `MappedBase`: Inherits async and declarative features
- **Abstract**: Marked as abstract, not instantiated directly
- **Benefits**: Combines dataclass conveniences with ORM capabilities

## Type Definitions

### Primary Key Type
```python
id_key = Annotated[
    int, 
    mapped_column(
        primary_key=True, 
        index=True, 
        autoincrement=True, 
        sort_order=-999, 
        comment='主键id'
    )
]
```
- **Purpose**: Reusable type annotation for primary key columns
- **Configuration**: 
  - `primary_key=True`: Marks as table primary key
  - `index=True`: Creates database index for performance
  - `autoincrement=True`: Automatic ID generation
  - `sort_order=-999`: Controls column ordering in representations
  - `comment`: Database-level documentation

## File Information Model

### `FileInfo` Class
```python
class FileInfo(DataClassBase):
    """文档信息"""
    __tablename__ = 'file_info'
```
- **Purpose**: Database model for file metadata storage
- **Table Name**: Explicitly set to 'file_info' (overrides automatic naming)
- **Base Class**: Inherits dataclass and SQLAlchemy ORM features

### Field Definitions

#### Primary Key
```python
id: Mapped[id_key] = mapped_column(init=False)
```
- **Type**: Uses the predefined `id_key` type annotation
- **Initialization**: `init=False` excludes from dataclass __init__ method
- **Purpose**: Auto-generated unique identifier

#### File Metadata
```python
filename: Mapped[str] = mapped_column(String(20), comment='文件名')
request_id: Mapped[str] = mapped_column(String(255), comment='请求id')
description: Mapped[str | None] = mapped_column(String(255), comment='描述')
file_path: Mapped[str] = mapped_column(String(50), comment='本地存储')
file_size: Mapped[int] = mapped_column(comment='文件大小')
```

- **filename**: 
  - **Type**: String with 20 character limit
  - **Purpose**: Original file name
  - **Required**: Non-nullable field

- **request_id**: 
  - **Type**: String with 255 character limit
  - **Purpose**: Associates file with specific request/session
  - **Required**: Non-nullable field

- **description**: 
  - **Type**: Optional string (255 characters)
  - **Purpose**: Human-readable file description
  - **Nullable**: Can be None/NULL

- **file_path**: 
  - **Type**: String with 50 character limit
  - **Purpose**: Local filesystem path
  - **Required**: Non-nullable field

- **file_size**: 
  - **Type**: Integer
  - **Purpose**: File size in bytes
  - **Required**: Non-nullable field

#### Status and Timestamp
```python
status: Mapped[int] = mapped_column(default=1, comment='文件状态(0删除 1正常)')
create_time: Mapped[datetime] = mapped_column(
    init=False,
    server_default=func.now(),
    comment='创建时间'
)
```

- **status**: 
  - **Type**: Integer with default value 1
  - **Purpose**: File status tracking (0=deleted, 1=normal)
  - **Default**: 1 (normal/active status)

- **create_time**: 
  - **Type**: DateTime
  - **Initialization**: `init=False` (not in dataclass constructor)
  - **Server Default**: `func.now()` generates timestamp at database level
  - **Purpose**: Automatic timestamp for record creation

## Advanced Features

### Modern SQLAlchemy Patterns
- **Mapped Type Annotations**: Uses `Mapped[Type]` for type safety
- **mapped_column()**: Modern column definition syntax
- **Automatic Imports**: Leverages SQLAlchemy 2.0+ features

### Dataclass Integration
- **Automatic Methods**: Dataclass provides __init__, __repr__, __eq__
- **Type Hints**: Full type checking support
- **Selective Initialization**: Some fields excluded from __init__ via `init=False`

### Database Features
- **Comments**: All columns include Chinese documentation
- **String Limits**: Appropriate length limits for different field types
- **Server Defaults**: Database-level timestamp generation
- **Status Tracking**: Built-in soft delete capability

## Comparison with file_table.py

### Similarities
- Both models represent file information
- Similar field structure and purpose
- Support for timestamps and status tracking

### Differences

#### Technology Stack
- **file_table.py**: Uses SQLModel (simpler, Pydantic integration)
- **file_info.py**: Uses pure SQLAlchemy 2.0+ (more advanced, native ORM)

#### Field Constraints
- **file_table.py**: More flexible field sizes, some optional fields
- **file_info.py**: Stricter length limits, more required fields

#### Base Classes
- **file_table.py**: Direct SQLModel inheritance
- **file_info.py**: Custom declarative base hierarchy

#### Default Values
- **file_table.py**: Status defaults to 0
- **file_info.py**: Status defaults to 1

## Usage Patterns

### Creating Records
```python
# Dataclass-style initialization
file_info = FileInfo(
    filename="document.pdf",
    request_id="req_123",
    description="Important document",
    file_path="/storage/document.pdf",
    file_size=1024000
)

# Database operations
async with async_session() as session:
    session.add(file_info)
    await session.commit()
```

### Querying Records
```python
# Using modern SQLAlchemy syntax
from sqlalchemy import select

async with async_session() as session:
    stmt = select(FileInfo).where(FileInfo.request_id == "req_123")
    result = await session.execute(stmt)
    files = result.scalars().all()
```

### Status Management
```python
# Soft delete by status
file_info.status = 0  # Mark as deleted

# Filter by status
stmt = select(FileInfo).where(FileInfo.status == 1)  # Only active files
```

## Technical Advantages

### Type Safety
- Full MyPy/PyChance compatibility
- Runtime type checking possible
- Clear field type specifications

### Performance
- Automatic indexing on primary key
- Appropriate string length limits
- Server-side timestamp generation

### Maintainability
- Clear separation of concerns
- Documented fields with comments
- Consistent naming patterns

### Async Support
- Native async/await support
- Efficient concurrent operations
- Modern SQLAlchemy async patterns