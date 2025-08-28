# genie_tool/model/context.py Code Documentation

## File Summary

This module provides context management and LLM model information systems for the Genie Tool. It includes request ID tracking using Python's context variables and a comprehensive model information factory for managing different LLM model specifications including context lengths and output limits.

## Request Context Management

### `_RequestIdCtx` Class
- **Purpose**: Manages request ID context across async operations using contextvars
- **Pattern**: Singleton class for global request context management

#### Constructor
```python
def __init__(self):
    self._request_id = contextvars.ContextVar("request_id", default="default-request-id")
```
- **Context Variable**: Uses Python's contextvars for async-safe context management
- **Default Value**: "default-request-id" when no context is set
- **Thread Safety**: contextvars automatically handle async context isolation

#### Properties
```python
@property
def request_id(self):
    return self._request_id.get()

@request_id.setter
def request_id(self, value):
    self._request_id.set(value)
```
- **Getter**: Retrieves current request ID from context
- **Setter**: Sets request ID in current context
- **Context Isolation**: Each async task maintains separate request ID

### RequestIdCtx Singleton
```python
RequestIdCtx = _RequestIdCtx()
```
- **Global Instance**: Single instance for application-wide request tracking
- **Usage**: Import and use across modules for consistent request identification

## LLM Model Information System

### `LLMModelInfo` Class
```python
class LLMModelInfo(BaseModel):
    model: str
    context_length: int
    max_output: int
```

#### Purpose
Pydantic model for storing LLM specifications and capabilities.

#### Fields
- **model** (`str`): 
  - **Purpose**: Unique identifier for the LLM model
  - **Usage**: Used for model selection and configuration lookup

- **context_length** (`int`): 
  - **Purpose**: Maximum context window size in tokens
  - **Usage**: Determines how much text can be processed in a single request

- **max_output** (`int`): 
  - **Purpose**: Maximum output tokens the model can generate
  - **Usage**: Controls response length and prevents truncation

### `_LLMModelInfoFactory` Class
- **Purpose**: Centralized registry and lookup system for LLM model information
- **Pattern**: Factory pattern with registration and retrieval methods

#### Constructor
```python
def __init__(self):
    self._factory = {}
```
- **Storage**: Dictionary mapping model names to LLMModelInfo objects
- **Initialization**: Empty registry, populated via registration

#### `register(model_info: LLMModelInfo)`
- **Purpose**: Adds new model information to the factory registry
- **Parameters**: 
  - `model_info`: LLMModelInfo object containing model specifications
- **Logic**: Stores model info indexed by model name
- **Usage**: Called during application initialization to populate model registry

#### `get_context_length(model: str, default: int = 128000) -> int`
- **Purpose**: Retrieves context length for specified model
- **Parameters**: 
  - `model`: Model identifier string
  - `default`: Fallback value if model not found (default: 128000)
- **Returns**: Context length in tokens
- **Logic**: 
  - Looks up model in registry
  - Returns registered context length if found
  - Returns default value if model not registered

#### `get_max_output(model: str, default: int = 32000) -> int`
- **Purpose**: Retrieves maximum output tokens for specified model
- **Parameters**: 
  - `model`: Model identifier string
  - `default`: Fallback value if model not found (default: 32000)
- **Returns**: Maximum output tokens
- **Logic**: 
  - Looks up model in registry
  - Returns registered max output if found
  - Returns default value if model not registered

### LLMModelInfoFactory Singleton
```python
LLMModelInfoFactory = _LLMModelInfoFactory()
```
- **Global Instance**: Single factory instance for application-wide model management
- **Pre-registration**: Includes predefined model configurations

## Predefined Model Configurations

### GPT-4.1 Model
```python
LLMModelInfoFactory.register(LLMModelInfo(model="gpt-4.1", context_length=1000000, max_output=32000))
```
- **Context Window**: 1,000,000 tokens (very large context)
- **Max Output**: 32,000 tokens
- **Usage**: High-capacity model for complex tasks

### DeepSeek-V3 Model
```python
LLMModelInfoFactory.register(LLMModelInfo(model="DeepSeek-V3", context_length=64000, max_output=8000))
```
- **Context Window**: 64,000 tokens (standard large context)
- **Max Output**: 8,000 tokens  
- **Usage**: Efficient model with good capabilities

## Usage Patterns

### Request Context Management
```python
# Setting request context
RequestIdCtx.request_id = "user-request-123"

# Retrieving in another function
current_request = RequestIdCtx.request_id  # "user-request-123"

# Automatic context isolation in async
async def handler1():
    RequestIdCtx.request_id = "req-1"
    await some_operation()  # Context preserved

async def handler2():
    RequestIdCtx.request_id = "req-2" 
    await some_operation()  # Separate context
```

### Model Information Lookup
```python
# Get context length with fallback
context_size = LLMModelInfoFactory.get_context_length("gpt-4.1")  # 1000000
context_size = LLMModelInfoFactory.get_context_length("unknown-model")  # 128000 (default)

# Get max output with custom default
max_tokens = LLMModelInfoFactory.get_max_output("DeepSeek-V3", default=16000)  # 8000
```

### Adding New Models
```python
# Register custom model
custom_model = LLMModelInfo(
    model="custom-llm-v1",
    context_length=32000,
    max_output=4000
)
LLMModelInfoFactory.register(custom_model)
```

## Technical Features

### Context Variable Benefits
- **Async Safety**: Automatically handles context isolation across async tasks
- **No Threading Issues**: Safe for concurrent request processing
- **Clean API**: Simple get/set interface without manual context passing
- **Automatic Cleanup**: Context automatically cleared when task completes

### Factory Pattern Advantages
- **Centralized Configuration**: Single source of truth for model specifications
- **Runtime Registration**: Models can be added dynamically
- **Fallback Handling**: Graceful degradation for unknown models
- **Type Safety**: Pydantic validation for model information

### Performance Considerations
- **Dictionary Lookup**: O(1) model information retrieval
- **Minimal Overhead**: Lightweight context variable operations
- **Lazy Evaluation**: Models registered only when needed

## Integration Points

### Request Tracking
- Used across API endpoints for consistent request identification
- Enables request-specific logging and debugging
- Supports request lifecycle management

### Token Management
- Critical for LLM request planning and optimization
- Prevents context overflow and truncation issues
- Enables intelligent content splitting and batching

### Model Selection
- Supports dynamic model selection based on requirements
- Enables model-specific optimizations and configurations
- Facilitates A/B testing and model comparison

## Error Handling
- **Missing Models**: Graceful fallback to default values
- **Context Isolation**: Automatic context cleanup prevents leaks
- **Type Validation**: Pydantic ensures model information correctness