"""
Deep search tool for searching internal and external knowledge.
搜索工具，可以通过搜索内外网知识
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from ..base_tool import BaseTool
from ...dto.deep_search_request import DeepSearchRequest
from ...dto.deep_search_response import DeepSearchResponse
from ...dto.file_request import FileRequest
from .file_tool import FileTool
from ...util.dependency_container import DependencyContainer
from ...util.string_util import StringUtil

logger = logging.getLogger(__name__)


class DeepSearchTool(BaseTool):
    """Deep search tool for searching internal and external knowledge."""
    
    def __init__(self):
        self.agent_context = None
    
    def get_name(self) -> str:
        return "deep_search"
    
    def get_description(self) -> str:
        desc = "这是一个搜索工具，可以通过搜索内外网知识"
        config = DependencyContainer.get_config()
        return config.deep_search_tool_desc if config.deep_search_tool_desc else desc
    
    def to_params(self) -> Dict[str, Any]:
        config = DependencyContainer.get_config()
        if config.deep_search_tool_params:
            return config.deep_search_tool_params
        
        task_param = {
            "type": "string", 
            "description": "需要搜索的query"
        }
        
        parameters = {
            "type": "object",
            "properties": {
                "query": task_param
            },
            "required": ["query"]
        }
        
        return parameters
    
    def execute(self, input_data: Any) -> Any:
        start_time = asyncio.get_event_loop().time()
        
        try:
            config = DependencyContainer.get_config()
            params = input_data if isinstance(input_data, dict) else {}
            query = params.get("query", "")
            
            src_config = {
                "bing": {
                    "count": int(config.deep_search_page_count)
                }
            }
            
            request = DeepSearchRequest(
                request_id=f"{self.agent_context.request_id}:{StringUtil.generate_random_string(5)}",
                query=query,
                agent_id="1",
                scene_type="auto_agent",
                src_configs=src_config,
                stream=True,
                content_stream=self.agent_context.is_stream
            )
            
            # 调用流式 API
            return asyncio.run(self._call_deep_search_stream(request))
            
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} deep_search agent error", exc_info=e)
        return None
    
    async def _call_deep_search_stream(self, search_request: DeepSearchRequest) -> str:
        """调用 DeepSearch"""
        try:
            config = DependencyContainer.get_config()
            url = f"{config.deep_search_url}/v1/tool/deepsearch"
            
            timeout = httpx.Timeout(connect=60.0, read=300.0, write=300.0, pool=300.0)
            
            logger.info(f"{self.agent_context.request_id} deep_search request {json.dumps(search_request.dict())}")
            
            interval = config.message_interval.get("search", "5,20").split(",")
            first_interval = int(interval[0])
            send_interval = int(interval[1])
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=search_request.dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if not response.is_success:
                        logger.error(f"{self.agent_context.request_id} deep_search request error")
                        raise Exception(f"Unexpected response code: {response.status_code}")
                    
                    logger.info(f"{self.agent_context.request_id} deep_search response {response.status_code}")
                    
                    index = 1
                    string_builder_incr = []
                    string_builder_all = []
                    digital_employee = self.agent_context.tool_collection.get_digital_employee(self.get_name())
                    result = "搜索结果为空"  # 默认输出
                    message_id = ""
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break
                            if data.startswith("heartbeat"):
                                continue
                            
                            if index == 1 or index % 100 == 0:
                                logger.info(f"{self.agent_context.request_id} deep_search recv data: {data}")
                            
                            search_response = DeepSearchResponse.parse_raw(data)
                            file_tool = FileTool()
                            file_tool.set_agent_context(self.agent_context)
                            
                            # 上传搜索内容到文件中
                            if search_response.is_final:
                                if self.agent_context.is_stream:
                                    search_response.answer = "".join(string_builder_all)
                                
                                if not search_response.answer:
                                    logger.error(f"{self.agent_context.request_id} deep search answer empty")
                                    break
                                
                                file_name = StringUtil.remove_special_chars(f"{search_response.query}的搜索结果.md")
                                file_desc = search_response.answer[:min(len(search_response.answer), config.deep_search_tool_file_desc_truncate_len)] + "..."
                                
                                file_request = FileRequest(
                                    request_id=self.agent_context.request_id,
                                    file_name=file_name,
                                    description=file_desc,
                                    content=search_response.answer
                                )
                                file_tool.upload_file(file_request, False, False)
                                result = search_response.answer[:min(len(search_response.answer), config.deep_search_tool_message_truncate_len)]
                                
                                self.agent_context.printer.send(message_id, "deep_search", search_response, digital_employee, True)
                                
                            else:
                                content_map = {}
                                for idx in range(len(search_response.search_result.query)):
                                    content_map[search_response.search_result.query[idx]] = search_response.search_result.docs[idx]
                                
                                if search_response.message_type == "extend":
                                    message_id = StringUtil.get_uuid()
                                    search_response.search_finish = False
                                    self.agent_context.printer.send(message_id, "deep_search", search_response, digital_employee, True)
                                
                                elif search_response.message_type == "search":
                                    search_response.search_finish = True
                                    self.agent_context.printer.send(message_id, "deep_search", search_response, digital_employee, True)
                                    file_request = FileRequest(
                                        request_id=self.agent_context.request_id,
                                        file_name=f"{search_response.query}_search_result.txt",
                                        description=f"{search_response.query}...",
                                        content=json.dumps(content_map)
                                    )
                                    file_tool.upload_file(file_request, False, True)
                                
                                elif search_response.message_type == "report":
                                    if index == 1:
                                        message_id = StringUtil.get_uuid()
                                    string_builder_incr.append(search_response.answer)
                                    string_builder_all.append(search_response.answer)
                                    if index == first_interval or index % send_interval == 0:
                                        search_response.answer = "".join(string_builder_incr)
                                        self.agent_context.printer.send(message_id, "deep_search", search_response, digital_employee, False)
                                        string_builder_incr.clear()
                                    index += 1
                    
                    return result
                    
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} deep_search request error", exc_info=e)
            raise
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context