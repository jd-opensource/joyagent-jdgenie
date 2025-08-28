# Tool Files Code Documentation

## genie_tool/tool/ci_agent.py

### File Summary
Custom code interpreter agent extending smolagents.CodeAgent with enhanced streaming, file handling, and execution management.

### Key Components
- **`CIAgent` Class**: Extended CodeAgent with custom streaming and file output
- **`_step_stream()` Method**: Core execution loop with streaming support
  - Handles model generation with stream deltas
  - Processes code parsing and execution
  - Yields CodeOutput and ActionOutput objects
  - Integrates FinalAnswerCheck for completion detection
- **Features**: Rich console integration, Live updates, comprehensive error handling

## genie_tool/tool/code_interpreter.py

### File Summary
High-level code interpreter functionality providing file processing, agent creation, and task execution.

### Key Functions
- **`code_interpreter_agent()`**: Main async function for code interpretation
  - File download and processing (Excel, CSV, text files)
  - Temporary directory management
  - Agent creation and task execution
  - Streaming response handling
  - File upload integration
- **`create_ci_agent()`**: Factory for creating configured CIAgent instances
- **`get_new_file_by_path()`**: Utility for finding latest generated files

### Features
- Pandas integration for data file processing
- Jinja2 templating for dynamic prompts
- Comprehensive file format support
- Automatic cleanup and resource management

## genie_tool/tool/deepsearch.py

### File Summary
Advanced web search system with AI-powered query processing, multi-engine support, and iterative reasoning.

### Key Components
- **`DeepSearch` Class**: Main orchestrator for deep search operations
  - Multi-engine search support (Bing, Jina, Sogou, SERP)
  - Iterative search loops with reasoning validation
  - Document deduplication and management
  - Streaming JSON responses
- **Key Methods**:
  - `run()`: Main search execution with streaming
  - `_search_queries_and_dedup()`: Parallel search with deduplication
  - `search_docs_str()`: Document formatting for LLM consumption

### Features
- Concurrent search execution using ThreadPoolExecutor
- Intelligent query decomposition
- Context-aware token management
- Real-time streaming updates

## genie_tool/tool/report.py

### File Summary
Comprehensive report generation system supporting multiple formats (HTML, Markdown, PPT) with intelligent content processing.

### Key Functions
- **`report()`**: Main entry point with format routing
- **`ppt_report()`**: PowerPoint-style HTML report generation
- **`markdown_report()`**: Markdown format report creation
- **`html_report()`**: Rich HTML report with structured content

### Features
- Template-based report generation using Jinja2
- Intelligent file filtering and content extraction
- Search result parsing and flattening
- Token-aware content truncation
- Multi-format output support
- Structured content organization (key files vs supplementary files)

### Content Processing
- Automatic file type detection
- Search result structure parsing
- Content truncation based on model limits
- Metadata extraction and categorization