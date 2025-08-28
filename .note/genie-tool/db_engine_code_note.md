# genie_tool/db/db_engine.py Code Documentation

## File Summary

This module provides database engine configuration and session management for the Genie Tool application. It sets up both synchronous and asynchronous SQLite database connections using SQLAlchemy, configures connection pooling, and provides utilities for database initialization and session management. The module supports FastAPI dependency injection patterns for database sessions.

## Database Configuration

### Connection Settings
- **Database Type**: SQLite
- **Database File**: Configurable via `SQLITE_DB_PATH` environment variable (default: "autobots.db")
- **Connection Pooling**: AsyncAdaptedQueuePool for async connections
- **Pool Configuration**: 10 connections, 3600-second recycle time

## Database Engines

### Synchronous Engine
```python
engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=True)
```
- **Purpose**: Synchronous database operations and table creation
- **Configuration**: 
  - Echo mode enabled for SQL logging
  - Direct SQLite connection string
- **Usage**: Primarily for database initialization and schema creation

### Asynchronous Engine
```python
async_engine = create_async_engine(
    f"sqlite+aiosqlite:///{SQLITE_DB_PATH}",
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    pool_recycle=3600,
    echo=False,
)
```
- **Purpose**: Asynchronous database operations for web requests
- **Configuration**: 
  - Uses aiosqlite for async SQLite support
  - Connection pooling with 10 connections
  - 1-hour connection recycling
  - Echo disabled for production performance
- **Usage**: Primary engine for all async database operations

## Session Management

### Async Session Factory
```python
async_session_local: Callable[..., AsyncSession] = sessionmaker(bind=async_engine, class_=AsyncSession)
```
- **Purpose**: Creates configured async session instances
- **Type**: Callable that returns AsyncSession objects
- **Binding**: Connected to the async_engine
- **Usage**: Factory for creating database sessions

### Session Generator Function
```python
async def get_async_session() -> AsyncGenerator[AsyncSession, None]
```
- **Purpose**: Provides async session generator for FastAPI dependency injection
- **Parameters**: None
- **Returns**: AsyncGenerator yielding AsyncSession instances
- **Key Logic**: 
  - Creates session using async_session_local factory
  - Uses async context manager for proper session cleanup
  - Automatically handles session lifecycle (open/close)
- **Usage Pattern**: Used as FastAPI Depends() parameter for route functions

## Database Initialization

### `init_db()`
- **Purpose**: Initializes database schema by creating all tables
- **Parameters**: None  
- **Returns**: None
- **Key Logic**: 
  - Imports FileInfo model to ensure table definition is loaded
  - Uses SQLModel.metadata.create_all() with synchronous engine
  - Logs successful initialization
  - Creates all tables defined in imported models
- **Usage**: Should be called once during application startup or setup

## Environment Variables

### `SQLITE_DB_PATH`
- **Purpose**: Specifies the SQLite database file location
- **Default**: "autobots.db" (in current working directory)
- **Format**: Relative or absolute file path
- **Example**: "/var/data/genie_tool.db"

## Dependencies

### Core Libraries
- **sqlalchemy**: ORM and database toolkit
- **sqlalchemy.ext.asyncio**: Async SQLAlchemy support
- **sqlmodel**: Modern SQLAlchemy wrapper with Pydantic integration
- **loguru**: Logging functionality

### Database Driver
- **aiosqlite**: Async SQLite driver for Python
- **sqlite**: Built-in SQLite support (for sync operations)

## Usage Patterns

### FastAPI Integration
```python
@app.get("/endpoint")
async def endpoint(session: AsyncSession = Depends(get_async_session)):
    # Use session for database operations
    pass
```

### Manual Session Usage
```python
async with async_session_local() as session:
    # Perform database operations
    result = await session.execute(select(FileInfo))
    await session.commit()
```

### Database Initialization
```python
# During application startup
from genie_tool.db.db_engine import init_db
init_db()
```

## Technical Features

### Connection Pooling Benefits
- **Performance**: Reuses connections instead of creating new ones
- **Resource Management**: Limits concurrent database connections
- **Stability**: Handles connection recycling to prevent stale connections

### Async/Await Support
- **Non-blocking**: Database operations don't block the event loop
- **Concurrency**: Multiple requests can access database simultaneously
- **Scalability**: Better performance under high load conditions

### Session Management
- **Automatic Cleanup**: Sessions are properly closed after use
- **Exception Handling**: Context managers handle errors gracefully
- **Thread Safety**: Each request gets its own session instance

## Main Execution Block
```python
if __name__ == "__main__":
    init_db()
```
- Allows direct execution for database initialization
- Useful for setup scripts and development workflows
- Creates database schema when run as standalone script

## Best Practices Implemented

1. **Environment Configuration**: Database path configurable via environment variables
2. **Connection Pooling**: Efficient resource utilization
3. **Async Support**: Modern async/await patterns
4. **Proper Session Management**: Context managers for cleanup
5. **Logging**: Database initialization logging for monitoring
6. **Separation of Concerns**: Sync engine for setup, async for operations