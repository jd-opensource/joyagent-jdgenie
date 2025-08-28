# Java to Python DTO Conversion

This directory contains Python equivalents of all Java DTOs and data models from genie-backend.

## Directory Structure

```
genie-backend-python/
├── src/main/python/com/jd/genie/
│   ├── agent/
│   │   ├── dto/
│   │   │   ├── tool/
│   │   │   │   ├── mcp_tool_info.py
│   │   │   │   ├── tool.py
│   │   │   │   ├── tool_call.py
│   │   │   │   ├── tool_choice.py
│   │   │   │   └── tool_result.py
│   │   │   ├── code_interpreter_request.py
│   │   │   ├── code_interpreter_response.py
│   │   │   ├── deep_search_request.py
│   │   │   ├── deep_search_response.py
│   │   │   ├── file.py
│   │   │   ├── file_request.py
│   │   │   ├── file_response.py
│   │   │   ├── memory.py
│   │   │   ├── message.py
│   │   │   ├── plan.py
│   │   │   ├── search_response.py
│   │   │   └── task_summary_result.py
│   │   └── enums/
│   │       └── role_type.py
│   └── model/
│       ├── dto/
│       │   ├── auto_bots_result.py
│       │   └── file_information.py
│       ├── multi/
│       │   ├── event_message.py
│       │   └── event_result.py
│       ├── req/
│       │   ├── agent_request.py
│       │   └── gpt_query_req.py
│       └── response/
│           ├── agent_response.py
│           └── gpt_process_result.py
├── requirements.txt
└── CONVERSION_README.md
```

## Conversion Details

### Key Changes Made:

1. **Framework**: Converted from Lombok annotations to Pydantic models
2. **Naming**: Converted Java camelCase to Python snake_case for field names
3. **Types**: Used Python type hints with Optional for nullable fields
4. **Enums**: Converted Java enums to Python Enum classes with utility methods
5. **Methods**: Converted Java methods to Python methods maintaining the same functionality
6. **Static Methods**: Converted Java static methods to @classmethod or @staticmethod
7. **Builder Pattern**: Leveraged Pydantic's built-in model creation instead of explicit builders

### Field Naming Conversions:

- `requestId` → `request_id`
- `fileName` → `file_name`
- `fileSize` → `file_size`
- `ossUrl` → `oss_url`
- `domainUrl` → `domain_url`
- `toolCallId` → `tool_call_id`
- `toolCalls` → `tool_calls`
- `base64Image` → `base64_image`
- `stepStatus` → `step_status`
- `messageType` → `message_type`
- And so on...

### Special Handling:

1. **Memory Class**: Maintained all Java functionality including tool context clearing
2. **Plan Class**: Preserved all step management and formatting methods
3. **ToolResult Class**: Maintained the ExecutionStatus enum and all utility methods
4. **EventResult Class**: Simplified complex Java concurrent operations while maintaining core functionality
5. **Message Class**: Preserved all static factory methods as classmethods

### Dependencies:

- **pydantic**: For data validation and serialization
- **typing-extensions**: For advanced type hints

### Usage Example:

```python
from com.jd.genie.agent.dto.message import Message
from com.jd.genie.agent.enums.role_type import RoleType

# Create a user message
message = Message.user_message("Hello, world!")

# Create a system message
system_msg = Message.system_message("System prompt")

# Direct instantiation
message = Message(
    role=RoleType.USER,
    content="Hello, world!",
    base64_image=None
)
```

## Installation

```bash
pip install -r requirements.txt
```

## Notes

- All files maintain the exact same data structure and validation logic as the original Java DTOs
- Python naming conventions are followed (snake_case for fields and methods)
- Pydantic provides automatic validation and serialization
- Type hints ensure better IDE support and runtime type checking
- All original functionality has been preserved while adapting to Python idioms