# genie_tool/model/document.py Code Documentation

## File Summary

This module defines the `Doc` dataclass for representing documents in the Genie Tool system, particularly for search results and document processing. The class provides structured data representation for web pages and other document types with comprehensive metadata, content management, and various output format methods.

## Doc Class

### Class Definition
```python
@dataclass
class Doc:
    """文档数据类"""
    doc_type: Literal["web_page"]
    content: str
    title: str
    link: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    unique_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    is_chunk: bool = False
    chunk_id: int = -1  # chunk标记
```

### Core Fields

#### Required Fields
- **doc_type** (`Literal["web_page"]`): 
  - **Purpose**: Specifies the type of document
  - **Current Support**: Only "web_page" is currently supported
  - **Usage**: Enables type-specific processing and display logic
  - **Extensibility**: Type literal can be expanded for future document types

- **content** (`str`): 
  - **Purpose**: Main text content of the document
  - **Usage**: Contains the actual document text for processing and analysis
  - **Format**: Plain text or structured text depending on source

- **title** (`str`): 
  - **Purpose**: Document title or name
  - **Usage**: Used for display, indexing, and identification
  - **Source**: Typically extracted from HTML title tags or document headers

#### Optional Fields with Defaults
- **link** (`str`, default: `""`): 
  - **Purpose**: URL or reference link to the original document
  - **Usage**: Enables navigation back to source, citation, and validation
  - **Default**: Empty string for documents without source URLs

- **data** (`dict[str, Any]`, default: `{}`): 
  - **Purpose**: Additional metadata or structured information
  - **Usage**: Extensible storage for document-specific data
  - **Examples**: Could contain extraction metadata, timestamps, source information

- **unique_id** (`str`, default: `UUID4`): 
  - **Purpose**: Unique identifier for the document instance
  - **Generation**: Automatically generated UUID4 string
  - **Usage**: Deduplication, tracking, and reference management

#### Chunking Fields
- **is_chunk** (`bool`, default: `False`): 
  - **Purpose**: Indicates whether this document is a chunk of a larger document
  - **Usage**: Supports document splitting and processing workflows
  - **Processing**: Enables different handling for chunks vs complete documents

- **chunk_id** (`int`, default: `-1`): 
  - **Purpose**: Identifier for chunk position or sequence
  - **Default**: -1 indicates not a chunk or unassigned
  - **Usage**: Maintains order and relationships between document chunks

## Methods

### `__str__() -> str`
- **Purpose**: Human-readable string representation of the document
- **Returns**: Formatted multi-line string with document information
- **Format**: 
  ```
  Doc(
    文档类型=网页,
    文档标题=Title Here,
    文档链接=https://example.com,
    文档内容=Content text here,
  )
  ```
- **Localization**: Uses Chinese labels for display
- **Type Mapping**: Converts "web_page" to "网页" for user-friendly display

### `to_html() -> str`
- **Purpose**: Generates HTML representation of the document
- **Returns**: HTML div with document information
- **Format**: 
  ```html
  <div>
    <p>文档类型:web_page</p>
    <p>文档标题:Title</p>
    <p>文档链接:https://example.com</p>
    <p>文档内容:Content</p>
  </div>
  ```
- **Usage**: Web display, report generation, HTML export

### `to_dict(truncate_len: int = 0) -> dict`
- **Purpose**: Converts document to dictionary format with optional content truncation
- **Parameters**: 
  - `truncate_len`: Maximum content length (0 = no truncation)
- **Returns**: Dictionary with all document fields
- **Logic**: 
  - Truncates content to specified length if `truncate_len > 0`
  - Includes all fields except chunking metadata
  - Maintains full content if no truncation specified
- **Usage**: JSON serialization, API responses, data export

## Design Patterns

### Dataclass Benefits
- **Automatic Methods**: __init__, __repr__, __eq__ automatically generated
- **Type Hints**: Clear type specifications for all fields
- **Immutability Option**: Can be made frozen for immutable documents
- **Field Defaults**: Flexible default values with factory functions

### UUID Generation
- **Uniqueness**: UUID4 provides cryptographically strong unique IDs
- **Collision Avoidance**: Extremely low probability of duplicates
- **Stateless**: No coordination required between instances
- **Factory Function**: Lambda ensures fresh UUID for each instance

### Type Safety
- **Literal Types**: Restricts doc_type to valid values
- **Generic Dict**: Flexible data field while maintaining type safety
- **Optional Fields**: Clear distinction between required and optional data

## Usage Patterns

### Creating Documents
```python
# Basic web page document
doc = Doc(
    doc_type="web_page",
    content="This is the main content of the web page...",
    title="Example Page Title",
    link="https://example.com/page"
)

# With additional metadata
doc = Doc(
    doc_type="web_page",
    content="Content here...",
    title="Research Article",
    link="https://journal.com/article",
    data={
        "author": "John Doe",
        "published": "2023-01-15",
        "category": "research"
    }
)
```

### Document Chunking
```python
# Create chunks from large document
original_doc = Doc(doc_type="web_page", content=long_content, title="Long Article")

chunks = []
for i, chunk_content in enumerate(split_content(long_content)):
    chunk = Doc(
        doc_type="web_page",
        content=chunk_content,
        title=f"{original_doc.title} (Part {i+1})",
        link=original_doc.link,
        is_chunk=True,
        chunk_id=i
    )
    chunks.append(chunk)
```

### Output Formats
```python
# String representation for logging
print(str(doc))

# HTML for web display
html_content = doc.to_html()

# Dictionary for JSON API
api_response = doc.to_dict(truncate_len=200)  # Truncate content to 200 chars
```

## Integration Points

### Search Systems
- Used by deep search functionality to represent search results
- Enables consistent document handling across different search engines
- Supports deduplication via unique_id and content comparison

### Content Processing
- Chunking support enables processing of large documents
- Metadata storage allows tracking of processing state
- Multiple output formats support different consumption patterns

### API Responses
- `to_dict()` method enables JSON serialization for REST APIs
- Truncation support optimizes response sizes
- Structured format enables consistent client-side processing

### Document Storage
- Unique IDs enable database storage and retrieval
- Metadata field supports extensible document attributes
- Link field maintains source relationships

## Technical Considerations

### Memory Efficiency
- Content truncation reduces memory usage for large documents
- Default factory functions prevent shared mutable defaults
- Optional fields minimize storage for unused attributes

### Extensibility
- Literal type can be expanded to support more document types
- Data dictionary provides flexible metadata storage
- Dataclass structure allows easy field additions

### Internationalization
- String representations use Chinese labels
- Could be extended with locale-specific formatting
- Content field supports Unicode text

### Performance
- UUID generation is fast but can be optimized if needed
- Dictionary conversion is efficient for serialization
- String methods are optimized for display use cases