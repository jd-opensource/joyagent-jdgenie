"""
SSE printer implementation for Server-Sent Events with FastAPI
"""
import json
import logging
import uuid
from typing import Any, Optional, Dict, AsyncGenerator
import re

from fastapi import Request
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse

from .printer import Printer
from ..enums.agent_type import AgentType
from ...model.response.agent_response import AgentResponse, Plan, ToolResult

logger = logging.getLogger(__name__)


class SSEPrinter(Printer):
    """
    SSE printer implementation for streaming responses via Server-Sent Events
    """
    
    def __init__(self, request: Any, agent_request: Any, agent_type: int):
        """
        Initialize SSE printer
        
        Args:
            request: FastAPI request object
            agent_request: Agent request object
            agent_type: Agent type value
        """
        self.request = request
        self.agent_request = agent_request
        self.agent_type = agent_type
        self._message_queue = []
        self._closed = False
    
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        digital_employee: Optional[str], 
        is_final: bool
    ) -> None:
        """
        Send a message via SSE
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
            is_final: Whether this is the final message
        """
        try:
            if message_id is None:
                message_id = self._generate_uuid()
            
            request_id = getattr(self.agent_request, 'request_id', 'unknown')
            logger.info(f"{request_id} sse send {message_type} {message} {digital_employee}")
            
            finish = message_type == "result"
            result_map = {"agentType": self.agent_type}
            
            response = AgentResponse(
                request_id=getattr(self.agent_request, 'request_id', None),
                message_id=message_id,
                message_type=message_type,
                message_time=str(int(1000 * __import__('time').time())),  # Current timestamp in ms
                result_map=result_map,
                finish=finish,
                is_final=is_final
            )
            
            if digital_employee:
                response.digital_employee = digital_employee
            
            # Handle different message types
            if message_type == "tool_thought":
                response.tool_thought = str(message)
            elif message_type == "task":
                # Remove execution order prefix
                task_content = re.sub(r"^执行顺序(\d+)\.\s?", "", str(message))
                response.task = task_content
            elif message_type == "task_summary":
                if isinstance(message, dict):
                    task_summary = message.get("taskSummary")
                    response.result_map = message
                    response.task_summary = str(task_summary) if task_summary else None
                else:
                    logger.error("ssePrinter task_summary format is illegal")
            elif message_type == "plan_thought":
                response.plan_thought = str(message)
            elif message_type == "plan":
                if hasattr(message, '__dict__'):
                    # Convert object to Plan
                    plan = Plan()
                    for attr_name, attr_value in message.__dict__.items():
                        if hasattr(plan, attr_name):
                            setattr(plan, attr_name, attr_value)
                    response.plan = AgentResponse.format_steps(plan)
                else:
                    response.plan = message
            elif message_type == "tool_result":
                response.tool_result = message if isinstance(message, ToolResult) else ToolResult(**message)
            elif message_type in ["browser", "code", "html", "markdown", "ppt", "file", "knowledge", "deep_search"]:
                if isinstance(message, str):
                    try:
                        message_dict = json.loads(message)
                    except json.JSONDecodeError:
                        message_dict = {"content": message}
                else:
                    message_dict = message if isinstance(message, dict) else {"content": str(message)}
                
                message_dict["agentType"] = self.agent_type
                response.result_map = message_dict
            elif message_type == "agent_stream":
                response.result = str(message)
            elif message_type == "result":
                if isinstance(message, str):
                    response.result = message
                elif isinstance(message, dict):
                    task_summary = message.get("taskSummary")
                    response.result_map = message
                    response.result = str(task_summary) if task_summary else None
                else:
                    # Convert to dict and extract summary
                    message_dict = json.loads(json.dumps(message, default=str))
                    response.result_map = message_dict
                    response.result = str(message_dict.get("taskSummary", ""))
                
                if response.result_map:
                    response.result_map["agentType"] = self.agent_type
            
            # Add to message queue for streaming
            self._message_queue.append(response)
            
        except Exception as e:
            logger.error(f"sse send error: {e}")
    
    def send(self, message_type: str, message: Any) -> None:
        """
        Send a message with minimal parameters
        
        Args:
            message_type: Type of the message
            message: Message content
        """
        self.send(None, message_type, message, None, True)
    
    def send(self, message_type: str, message: Any, digital_employee: Optional[str]) -> None:
        """
        Send a message with digital employee
        
        Args:
            message_type: Type of the message
            message: Message content
            digital_employee: Digital employee identifier
        """
        self.send(None, message_type, message, digital_employee, True)
    
    def send(
        self, 
        message_id: Optional[str], 
        message_type: str, 
        message: Any, 
        is_final: bool
    ) -> None:
        """
        Send a message with message ID and final flag
        
        Args:
            message_id: Unique message identifier
            message_type: Type of the message
            message: Message content
            is_final: Whether this is the final message
        """
        self.send(message_id, message_type, message, None, is_final)
    
    def close(self) -> None:
        """
        Close the SSE connection
        """
        self._closed = True
    
    def update_agent_type(self, agent_type: AgentType) -> None:
        """
        Update the agent type
        
        Args:
            agent_type: New agent type
        """
        self.agent_type = agent_type.value
    
    async def stream_events(self) -> AsyncGenerator[str, None]:
        """
        Generate SSE events from the message queue
        
        Yields:
            SSE formatted event strings
        """
        try:
            while not self._closed:
                if self._message_queue:
                    response = self._message_queue.pop(0)
                    event_data = response.model_dump_json()
                    yield f"data: {event_data}\n\n"
                else:
                    # Check if client disconnected
                    if await self._is_client_disconnected():
                        break
                    # Small delay to prevent busy waiting
                    await __import__('asyncio').sleep(0.1)
        except Exception as e:
            logger.error(f"Error in stream_events: {e}")
        finally:
            yield "data: [DONE]\n\n"
    
    async def _is_client_disconnected(self) -> bool:
        """
        Check if the client has disconnected
        
        Returns:
            True if client disconnected, False otherwise
        """
        try:
            # This is a simplified check - in a real implementation,
            # you might want to use more sophisticated connection checking
            return False
        except Exception:
            return True
    
    def _generate_uuid(self) -> str:
        """
        Generate a UUID string
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    def get_event_source_response(self) -> EventSourceResponse:
        """
        Get FastAPI EventSourceResponse for SSE streaming
        
        Returns:
            EventSourceResponse object
        """
        return EventSourceResponse(
            self.stream_events(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "*"
            }
        )