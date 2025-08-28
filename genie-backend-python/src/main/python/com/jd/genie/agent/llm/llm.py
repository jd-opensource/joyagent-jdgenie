"""
LLM class for handling language model interactions
"""
import asyncio
import json
import logging
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable
import httpx
from copy import deepcopy

from .config import Config
from .llm_settings import LLMSettings
from .token_counter import TokenCounter
from ..dto.message import Message
from ..dto.tool.tool_call import ToolCall, Function
from ..dto.tool.tool_choice import ToolChoice

logger = logging.getLogger(__name__)


@dataclass
class ToolCallResponse:
    """LLM response class for tool calls"""
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = field(default_factory=list)
    finish_reason: Optional[str] = None
    total_tokens: Optional[int] = None
    duration: Optional[int] = None


@dataclass
class OpenAIChoice:
    """OpenAI API choice response structure"""
    index: Optional[int] = None
    delta: Optional['OpenAIDelta'] = None
    logprobs: Optional[Any] = None
    finish_reason: Optional[str] = None


@dataclass
class OpenAIDelta:
    """OpenAI API delta response structure"""
    content: Optional[str] = None
    tool_calls: Optional[List['OpenAIToolCall']] = field(default_factory=list)


@dataclass
class OpenAIToolCall:
    """OpenAI tool call structure"""
    index: Optional[int] = None
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional['OpenAIFunction'] = None


@dataclass
class OpenAIFunction:
    """OpenAI function structure"""
    name: Optional[str] = None
    arguments: Optional[str] = ""


@dataclass
class ClaudeResponse:
    """Claude API response structure"""
    delta: Optional['ClaudeDelta'] = None
    arguments: Optional[str] = None
    id: Optional[str] = None


@dataclass
class ClaudeDelta:
    """Claude delta response structure"""
    text: Optional[str] = None
    partial_json: Optional[str] = None
    type: Optional[str] = None


class LLM:
    """
    LLM class for handling language model interactions
    """
    
    _instances: Dict[str, 'LLM'] = {}
    
    def __init__(self, model_name: str, llm_erp: Optional[str] = None):
        """
        Initialize LLM instance
        
        Args:
            model_name: Name of the model to use
            llm_erp: LLM ERP identifier
        """
        self.llm_erp = llm_erp
        
        # Load configuration
        config = Config.get_llm_config(model_name)
        self.model = config.model
        self.max_tokens = config.max_tokens
        self.temperature = config.temperature
        self.api_key = config.api_key
        self.base_url = config.base_url
        self.interface_url = config.interface_url if config.interface_url else "/v1/chat/completions"
        self.function_call_type = config.function_call_type
        self.ext_params = config.ext_params or {}
        
        # Initialize token counting
        self.total_input_tokens = 0
        self.max_input_tokens = config.max_input_tokens
        
        # Initialize tokenizer
        self.token_counter = TokenCounter()
    
    @staticmethod
    def format_messages(messages: List[Message], is_claude: bool = False) -> List[Dict[str, Any]]:
        """
        Format messages for API consumption
        
        Args:
            messages: List of Message objects
            is_claude: Whether formatting for Claude API
            
        Returns:
            List of formatted message dictionaries
        """
        formatted_messages = []
        
        for message in messages:
            message_map = {}
            
            # Handle base64 images
            if message.base64_image:
                multimodal_content = []
                
                # Create image content
                image_url_map = {"url": f"data:image/jpeg;base64,{message.base64_image}"}
                image_content = {"type": "image_url", "image_url": image_url_map}
                multimodal_content.append(image_content)
                
                # Create text content
                text_content = {"type": "text", "text": message.content}
                multimodal_content.append(text_content)
                
                message_map["role"] = message.role.value
                message_map["content"] = multimodal_content
                
            elif message.tool_calls:
                if is_claude:
                    # Claude format tool calls
                    message_map["role"] = message.role.value
                    claude_tool_calls = []
                    for tool_call in message.tool_calls:
                        claude_tool_call = {
                            "type": "tool_use",
                            "id": tool_call.id,
                            "name": tool_call.function.name,
                            "input": json.loads(tool_call.function.arguments)
                        }
                        claude_tool_calls.append(claude_tool_call)
                    message_map["content"] = claude_tool_calls
                else:
                    # Standard OpenAI format
                    message_map["role"] = message.role.value
                    tool_calls_map = []
                    for tool_call in message.tool_calls:
                        tool_call_map = {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        tool_calls_map.append(tool_call_map)
                    message_map["tool_calls"] = tool_calls_map
                    
            elif message.tool_call_id:
                content = message.content  # TODO: Add sensitive word filtering
                if is_claude:
                    # Claude format tool results
                    message_map["role"] = "user"
                    claude_tool_calls = [{
                        "type": "tool_result",
                        "tool_use_id": message.tool_call_id,
                        "content": content
                    }]
                    message_map["content"] = claude_tool_calls
                else:
                    message_map["role"] = message.role.value
                    message_map["content"] = content
                    message_map["tool_call_id"] = message.tool_call_id
            else:
                message_map["role"] = message.role.value
                message_map["content"] = message.content
                
            formatted_messages.append(message_map)
            
        return formatted_messages
    
    def truncate_message(self, context: Any, messages: List[Dict[str, Any]], max_input_tokens: int) -> List[Dict[str, Any]]:
        """
        Truncate messages to fit within token limit
        
        Args:
            context: Agent context
            messages: List of formatted messages
            max_input_tokens: Maximum input tokens allowed
            
        Returns:
            Truncated list of messages
        """
        if not messages or max_input_tokens < 0:
            return messages
            
        logger.info(f"{getattr(context, 'request_id', 'unknown')} before truncate {json.dumps(messages)}")
        
        truncated_messages = []
        remaining_tokens = max_input_tokens
        
        # Reserve tokens for system message if present
        system_message = messages[0] if messages and messages[0].get("role") == "system" else None
        if system_message:
            remaining_tokens -= self.token_counter.count_message_tokens(system_message)
        
        # Add messages from end to beginning (keep most recent)
        for message in reversed(messages):
            if message.get("role") == "system":
                continue
                
            message_tokens = self.token_counter.count_message_tokens(message)
            if remaining_tokens >= message_tokens:
                truncated_messages.insert(0, message)
                remaining_tokens -= message_tokens
            else:
                break
        
        # Ensure completeness by removing leading non-user messages
        while truncated_messages and truncated_messages[0].get("role") != "user":
            truncated_messages.pop(0)
        
        # Add system message back if present
        if system_message:
            truncated_messages.insert(0, system_message)
            
        logger.info(f"{getattr(context, 'request_id', 'unknown')} after truncate {json.dumps(truncated_messages)}")
        return truncated_messages
    
    async def ask(
        self, 
        context: Any,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        stream: bool = False,
        temperature: Optional[float] = None
    ) -> str:
        """
        Send request to LLM and get response
        
        Args:
            context: Agent context
            messages: List of messages
            system_msgs: System messages
            stream: Whether to use streaming
            temperature: Temperature parameter
            
        Returns:
            LLM response text
        """
        try:
            # Format messages
            if system_msgs:
                formatted_system_msgs = self.format_messages(system_msgs, False)
                formatted_messages = formatted_system_msgs + self.format_messages(messages, "claude" in self.model)
            else:
                formatted_messages = self.format_messages(messages, "claude" in self.model)
            
            # Prepare request parameters
            params = {
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature if temperature is not None else self.temperature,
                "stream": stream,
                **self.ext_params
            }
            
            if self.llm_erp:
                params["erp"] = self.llm_erp
            
            logger.info(f"{getattr(context, 'request_id', 'unknown')} call llm ask request {json.dumps(params)}")
            
            if not stream:
                # Non-streaming request
                response = await self._call_openai(params)
                logger.info(f"{getattr(context, 'request_id', 'unknown')} call llm response {response}")
                
                response_json = json.loads(response)
                choices = response_json.get("choices", [])
                
                if not choices or not choices[0].get("message", {}).get("content"):
                    raise ValueError("Empty or invalid response from LLM")
                
                return choices[0]["message"]["content"]
            else:
                # Streaming request
                return await self._call_openai_stream(params)
                
        except Exception as e:
            logger.error(f"{getattr(context, 'request_id', 'unknown')} Unexpected error in ask: {e}")
            raise
    
    def deep_copy(self, original: Any) -> Any:
        """
        Create a deep copy of an object
        
        Args:
            original: Object to copy
            
        Returns:
            Deep copy of the object
        """
        return deepcopy(original)
    
    def gpt_to_claude_tool(self, gpt_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI GPT tool definitions to Claude tool format
        
        Args:
            gpt_tools: List of GPT format tool definitions
            
        Returns:
            List of Claude format tool definitions
        """
        new_gpt_tools = self.deep_copy(gpt_tools)
        claude_tools = []
        
        for gpt_tool_wrapper in new_gpt_tools:
            # Extract function object
            gpt_tool = gpt_tool_wrapper["function"]
            claude_tool = {
                "name": gpt_tool["name"],
                "description": gpt_tool["description"]
            }
            
            # Process parameters
            parameters = gpt_tool.get("parameters", {})
            
            # Add function_name to required fields
            new_required = ["function_name"]
            if "required" in parameters and parameters["required"]:
                new_required.extend(parameters["required"])
            parameters["required"] = new_required
            
            # Add function_name to properties
            new_properties = {
                "function_name": {
                    "description": f"默认值为工具名: {gpt_tool['name']}",
                    "type": "string"
                }
            }
            if "properties" in parameters and parameters["properties"]:
                new_properties.update(parameters["properties"])
            parameters["properties"] = new_properties
            
            claude_tool["input_schema"] = parameters
            claude_tools.append(claude_tool)
            
        return claude_tools
    
    def _add_function_name_param(self, parameters: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """
        Add function_name parameter to tool parameters
        
        Args:
            parameters: Original parameters
            tool_name: Name of the tool
            
        Returns:
            Updated parameters with function_name
        """
        new_parameters = self.deep_copy(parameters)
        
        # Add to required fields
        new_required = ["function_name"]
        if "required" in parameters and parameters["required"]:
            new_required.extend(parameters["required"])
        new_parameters["required"] = new_required
        
        # Add to properties
        new_properties = {
            "function_name": {
                "description": f"默认值为工具名: {tool_name}",
                "type": "string"
            }
        }
        if "properties" in parameters and parameters["properties"]:
            new_properties.update(parameters["properties"])
        new_parameters["properties"] = new_properties
        
        return new_parameters
    
    async def ask_tool(
        self,
        context: Any,
        messages: List[Message],
        system_msgs: Optional[Message] = None,
        tools: Any = None,  # ToolCollection
        tool_choice: ToolChoice = ToolChoice.AUTO,
        temperature: Optional[float] = None,
        stream: bool = False,
        timeout: int = 300
    ) -> ToolCallResponse:
        """
        Send tool request to LLM and get response
        
        Args:
            context: Agent context
            messages: List of messages
            system_msgs: System message
            tools: Tool collection
            tool_choice: Tool choice type
            temperature: Temperature parameter
            stream: Whether to use streaming
            timeout: Request timeout
            
        Returns:
            ToolCallResponse object
        """
        try:
            # Validate tool_choice
            if not ToolChoice.is_valid(tool_choice):
                raise ValueError(f"Invalid tool_choice: {tool_choice}")
            
            start_time = asyncio.get_event_loop().time()
            
            # Set up API request
            params = {}
            formatted_tools = []
            
            if self.function_call_type == "struct_parse":
                # Handle struct_parse function call type
                # TODO: Add struct_parse logic
                pass
            else:
                # Standard function_call
                if tools:
                    # Add base tools
                    for tool in tools.tool_map.values():
                        function_map = {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.to_params()
                        }
                        tool_map = {
                            "type": "function",
                            "function": function_map
                        }
                        formatted_tools.append(tool_map)
                    
                    # Add MCP tools
                    for tool in tools.mcp_tool_map.values():
                        parameters = json.loads(tool.parameters)
                        function_map = {
                            "name": tool.name,
                            "description": tool.desc,
                            "parameters": parameters
                        }
                        tool_map = {
                            "type": "function", 
                            "function": function_map
                        }
                        formatted_tools.append(tool_map)
                    
                    if "claude" in self.model:
                        formatted_tools = self.gpt_to_claude_tool(formatted_tools)
            
            # Format messages
            formatted_messages = []
            if system_msgs:
                if "claude" in self.model:
                    params["system"] = system_msgs.content
                else:
                    formatted_messages.extend(self.format_messages([system_msgs], "claude" in self.model))
            
            formatted_messages.extend(self.format_messages(messages, "claude" in self.model))
            
            params.update({
                "model": self.model,
                "messages": formatted_messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature if temperature is not None else self.temperature,
                "stream": stream,
                **self.ext_params
            })
            
            if self.llm_erp:
                params["erp"] = self.llm_erp
            
            if self.function_call_type != "struct_parse":
                params["tools"] = formatted_tools
                params["tool_choice"] = tool_choice.value
            
            logger.info(f"{getattr(context, 'request_id', 'unknown')} call llm request {json.dumps(params)}")
            
            if not stream:
                # Non-streaming request
                response_json = await self._call_openai(params, timeout)
                logger.info(f"{getattr(context, 'request_id', 'unknown')} call llm response {response_json}")
                
                response = json.loads(response_json)
                choices = response.get("choices", [])
                
                if not choices or not choices[0].get("message"):
                    logger.error(f"{getattr(context, 'request_id', 'unknown')} Invalid response: {response_json}")
                    raise ValueError("Invalid or empty response from LLM")
                
                # Extract response content
                message = choices[0]["message"]
                content = message.get("content") if message.get("content") != "null" else None
                
                # Extract tool calls
                tool_calls = []
                if self.function_call_type == "struct_parse":
                    # Handle struct_parse tool calls
                    pattern = r"```json\s*([\s\S]*?)\s*```"
                    matches = self._find_matches(content or "", pattern)
                    for match in matches:
                        tool_call = self._parse_tool_call(context, match)
                        if tool_call:
                            tool_calls.append(tool_call)
                    
                    # Remove JSON block from content
                    if content:
                        stop_pos = content.find("```json")
                        if stop_pos >= 0:
                            content = content[:stop_pos]
                else:
                    # Standard function calls
                    if "tool_calls" in message:
                        for tool_call_data in message["tool_calls"]:
                            tool_call = ToolCall(
                                id=tool_call_data["id"],
                                type=tool_call_data["type"],
                                function=Function(
                                    name=tool_call_data["function"]["name"],
                                    arguments=tool_call_data["function"]["arguments"]
                                )
                            )
                            tool_calls.append(tool_call)
                
                # Extract other information
                finish_reason = choices[0].get("finish_reason")
                total_tokens = response.get("usage", {}).get("total_tokens")
                
                end_time = asyncio.get_event_loop().time()
                duration = int((end_time - start_time) * 1000)
                
                return ToolCallResponse(
                    content=content,
                    tool_calls=tool_calls,
                    finish_reason=finish_reason,
                    total_tokens=total_tokens,
                    duration=duration
                )
            else:
                # Streaming request
                if "claude" in self.model:
                    return await self._call_claude_function_call_stream(context, params)
                else:
                    return await self._call_openai_function_call_stream(context, params)
                    
        except Exception as e:
            logger.error(f"{getattr(context, 'request_id', 'unknown')} Unexpected error in ask_tool: {e}")
            raise
    
    async def _call_openai(self, params: Dict[str, Any], timeout: int = 300) -> str:
        """
        Call OpenAI API
        
        Args:
            params: Request parameters
            timeout: Request timeout in seconds
            
        Returns:
            API response as string
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            api_endpoint = f"{self.base_url}{self.interface_url}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                api_endpoint,
                json=params,
                headers=headers
            )
            
            if not response.is_success:
                raise httpx.HTTPError(f"Unexpected response code: {response.status_code}")
            
            return response.text
    
    async def _call_openai_stream(self, params: Dict[str, Any]) -> str:
        """
        Call OpenAI streaming API
        
        Args:
            params: Request parameters
            
        Returns:
            Complete response text
        """
        collected_messages = []
        
        async with httpx.AsyncClient(timeout=300) as client:
            api_endpoint = f"{self.base_url}{self.interface_url}"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with client.stream(
                "POST",
                api_endpoint,
                json=params,
                headers=headers
            ) as response:
                
                if not response.is_success:
                    raise httpx.HTTPError(f"Unexpected response code: {response.status_code}")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and chunk["choices"]:
                                choice = chunk["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    content = choice["delta"]["content"]
                                    collected_messages.append(content)
                                    logger.info(f"recv data: {content}")
                        except json.JSONDecodeError:
                            # Ignore non-JSON data
                            pass
                
                full_response = "".join(collected_messages).strip()
                
                if not full_response:
                    raise ValueError("Empty response from streaming LLM")
                
                return full_response
    
    async def _call_openai_function_call_stream(self, context: Any, params: Dict[str, Any]) -> ToolCallResponse:
        """
        Call OpenAI function call streaming API
        
        Args:
            context: Agent context
            params: Request parameters
            
        Returns:
            ToolCallResponse object
        """
        # TODO: Implement streaming function call logic
        # This is a complex implementation that handles streaming tool calls
        # For now, return a basic implementation
        response = await self._call_openai(params)
        response_data = json.loads(response)
        
        return ToolCallResponse(
            content=response_data.get("choices", [{}])[0].get("message", {}).get("content"),
            tool_calls=[],
            finish_reason=response_data.get("choices", [{}])[0].get("finish_reason")
        )
    
    async def _call_claude_function_call_stream(self, context: Any, params: Dict[str, Any]) -> ToolCallResponse:
        """
        Call Claude function call streaming API
        
        Args:
            context: Agent context
            params: Request parameters
            
        Returns:
            ToolCallResponse object
        """
        # TODO: Implement Claude streaming function call logic
        # This is a complex implementation that handles Claude's specific streaming format
        # For now, return a basic implementation
        response = await self._call_openai(params)
        response_data = json.loads(response)
        
        return ToolCallResponse(
            content=response_data.get("choices", [{}])[0].get("message", {}).get("content"),
            tool_calls=[],
            finish_reason=response_data.get("choices", [{}])[0].get("finish_reason")
        )
    
    def _find_matches(self, text: str, pattern: str) -> List[str]:
        """
        Find regex matches in text
        
        Args:
            text: Text to search
            pattern: Regex pattern
            
        Returns:
            List of matched groups
        """
        matches = []
        for match in re.finditer(pattern, text):
            matches.append(match.group(1))
        return matches
    
    def _parse_tool_call(self, context: Any, json_content: str) -> Optional[ToolCall]:
        """
        Parse tool call JSON
        
        Args:
            context: Agent context
            json_content: JSON content string
            
        Returns:
            ToolCall object or None if parsing fails
        """
        try:
            json_obj = json.loads(json_content)
            tool_name = json_obj.pop("function_name")
            
            return ToolCall(
                id=str(uuid.uuid4()),
                function=Function(
                    name=tool_name,
                    arguments=json.dumps(json_obj)
                )
            )
        except Exception as e:
            logger.error(f"{getattr(context, 'request_id', 'unknown')} parse tool call error {json_content}: {e}")
            return None