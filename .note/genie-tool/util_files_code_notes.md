# Utility Files Code Documentation

## genie_tool/util/llm_util.py

### File Summary
Provides async LLM communication utilities using litellm library with streaming support and sensitive content filtering.

### Key Functions
- **`ask_llm()`**: Main async function for LLM requests
  - Supports both streaming and non-streaming responses
  - Handles message formatting and validation
  - Includes sensitive word replacement
  - Configurable temperature, top_p parameters
  - Timer-decorated for performance monitoring

## genie_tool/util/file_util.py

### File Summary
Comprehensive file management utilities for downloading, uploading, processing, and manipulating files across local and remote sources.

### Key Functions
- **`get_file_content()`**: Downloads file content from URLs or local paths
- **`download_all_files()`**: Batch file content retrieval with error handling
- **`truncate_files()`**: Intelligent content truncation for token limits
- **`upload_file()`**: Content-based file upload to file server
- **`upload_file_by_path()`**: Path-based file upload
- **`generate_data_id()`**: Secure random ID generation
- **`flatten_search_file()`**: Parses structured search results
- **`get_file_path()`**: Download and cache remote files locally

### Features
- Async HTTP operations using aiohttp
- Error handling and retry logic
- Multiple file format support
- Token-aware content management
- Secure random string generation

## genie_tool/util/prompt_util.py

### File Summary
Simple utility for loading YAML-based prompt templates from the package resources.

### Key Functions
- **`get_prompt(prompt_file)`**: Loads and parses YAML prompt templates
  - Uses importlib.resources for package-relative loading
  - Returns parsed YAML as Python dict
  - Supports template files in genie_tool.prompt package

### Usage Pattern
```python
template = get_prompt("code_interpreter")
# Loads genie_tool/prompt/code_interpreter.yaml
```