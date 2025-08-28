"""
Base agent response handler implementation.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..agent.enums.response_type_enum import ResponseTypeEnum
from ..model.constant.constants import Constants
from ..model.multi.event_message import EventMessage
from ..model.multi.event_result import EventResult
from ..model.req.agent_request import AgentRequest
from ..model.response.agent_response import AgentResponse
from ..model.response.gpt_process_result import GptProcessResult

logger = logging.getLogger(__name__)


class BaseAgentResponseHandler:
    """Base class for agent response handlers providing common functionality."""
    
    def build_incr_result(
        self,
        request: AgentRequest,
        event_result: EventResult,
        agent_response: AgentResponse
    ) -> GptProcessResult:
        """
        Build incremental result from agent response.
        
        Args:
            request: The agent request
            event_result: Event result object
            agent_response: Agent response to process
            
        Returns:
            Processed GPT result
        """
        stream_result = GptProcessResult()
        stream_result.response_type = ResponseTypeEnum.TEXT.name
        stream_result.status = Constants.SUCCESS if agent_response.finish else Constants.RUNNING
        stream_result.finished = agent_response.finish
        
        if agent_response.message_type == "result":
            stream_result.response = agent_response.result
            stream_result.response_all = agent_response.result
            
        stream_result.req_id = request.request_id
        
        agent_type = None
        if (agent_response.result_map is not None and 
            "agentType" in agent_response.result_map):
            agent_type = str(agent_response.result_map["agentType"])
        
        result_map: Dict[str, Any] = {
            "agentType": agent_type,
            "multiAgent": {},
            "eventData": {}
        }
        
        # Build incremental data message
        message = EventMessage(message_id=agent_response.message_id)
        
        is_final = agent_response.is_final is True
        is_filter_final = (
            agent_response.result_map is not None and
            agent_response.message_type == "deep_search" and
            "messageType" in agent_response.result_map and
            agent_response.result_map["messageType"] == "extend"
        )
        
        # Process different message types
        if agent_response.message_type == "plan_thought":
            message.message_type = agent_response.message_type
            message.message_order = event_result.get_and_incr_order(agent_response.message_type)
            message.result_map = json.loads(json.dumps(agent_response.__dict__))
            if is_final and "plan_thought" not in event_result.result_map:
                event_result.result_map["plan_thought"] = agent_response.plan_thought
                
        elif agent_response.message_type == "plan":
            if event_result.is_init_plan():
                # Plan generation
                message.message_type = agent_response.message_type
                message.message_order = 1
                message.result_map = agent_response.plan
                if is_final:
                    event_result.result_map["plan"] = agent_response.plan
            else:
                # Plan update, needs to associate with task
                message.task_id = event_result.task_id
                message.task_order = event_result.task_order.get_and_increment()
                message.message_type = "task"
                message.message_order = 1
                message.result_map = json.loads(json.dumps(agent_response.__dict__))
                if is_final:
                    event_result.set_result_map_sub_task(message.result_map)
                    
        elif agent_response.message_type == "task":
            message.task_id = event_result.renew_task_id()
            message.task_order = event_result.task_order.get_and_increment()
            message.message_type = agent_response.message_type
            message.message_order = 1
            message.result_map = json.loads(json.dumps(agent_response.__dict__))
            if is_final:
                task = [message.result_map]
                event_result.set_result_map_task(task)
                
        else:
            # Default case
            message.task_id = event_result.task_id
            message.task_order = event_result.task_order.get_and_increment()
            message.message_type = "task"
            message.message_order = 1
            
            if agent_response.message_type in event_result.stream_task_message_type:
                order_key = f"{event_result.task_id}:{agent_response.message_type}"
                message.message_order = event_result.get_and_incr_order(order_key)
                
            message.result_map = json.loads(json.dumps(agent_response.__dict__))
            if is_final and not is_filter_final:
                event_result.set_result_map_sub_task(message.result_map)
        
        # Set incremental cache
        result_map["eventData"] = json.loads(json.dumps(message.__dict__))
        stream_result.result_map = result_map
        
        return stream_result