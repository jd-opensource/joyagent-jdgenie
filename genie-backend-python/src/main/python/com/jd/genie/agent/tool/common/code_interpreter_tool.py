"""
Code interpreter tool for executing code and processing data.
代码工具，可以通过编写代码完成数据处理、数据分析、图表生成等任务
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from ..base_tool import BaseTool
from ...dto.code_interpreter_request import CodeInterpreterRequest
from ...dto.code_interpreter_response import CodeInterpreterResponse
from ...dto.file import File
from ...util.dependency_container import DependencyContainer

logger = logging.getLogger(__name__)


class CodeInterpreterTool(BaseTool):
    """Code interpreter tool for executing code and processing data."""
    
    def __init__(self):
        self.agent_context = None
    
    def get_name(self) -> str:
        return "code_interpreter"
    
    def get_description(self) -> str:
        desc = "这是一个代码工具，可以通过编写代码完成数据处理、数据分析、图表生成等任务"
        config = DependencyContainer.get_config()
        return config.code_agent_desc if config.code_agent_desc else desc
    
    def to_params(self) -> Dict[str, Any]:
        config = DependencyContainer.get_config()
        if config.code_agent_params:
            return config.code_agent_params
        
        task_param = {
            "type": "string",
            "description": "需要完成的任务以及完成任务需要的数据，需要尽可能详细"
        }
        
        parameters = {
            "type": "object",
            "properties": {
                "task": task_param
            },
            "required": ["task"]
        }
        
        return parameters
    
    def execute(self, input_data: Any) -> Any:
        try:
            params = input_data if isinstance(input_data, dict) else {}
            task = params.get("task", "")
            
            file_names = [file.file_name for file in self.agent_context.product_files]
            
            request = CodeInterpreterRequest(
                request_id=self.agent_context.session_id,  # 适配多轮对话
                query=self.agent_context.query,
                task=task,
                file_names=file_names,
                stream=True
            )
            
            # 调用流式 API
            return asyncio.run(self._call_code_agent_stream(request))
            
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} code agent error", exc_info=e)
        return None
    
    async def _call_code_agent_stream(self, code_request: CodeInterpreterRequest) -> str:
        """调用 CodeAgent"""
        try:
            config = DependencyContainer.get_config()
            url = f"{config.code_interpreter_url}/v1/tool/code_interpreter"
            
            timeout = httpx.Timeout(connect=60.0, read=300.0, write=300.0, pool=300.0)
            
            logger.info(f"{self.agent_context.request_id} code_interpreter request {json.dumps(code_request.dict())}")
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=code_request.dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if not response.is_success:
                        logger.error(f"{self.agent_context.request_id} code_interpreter request error")
                        raise Exception(f"Unexpected response code: {response.status_code}")
                    
                    logger.info(f"{self.agent_context.request_id} code_interpreter response {response.status_code}")
                    
                    code_response = CodeInterpreterResponse(
                        code_output="code_interpreter执行失败"  # 默认输出
                    )
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break
                            if data.startswith("heartbeat"):
                                continue
                            
                            logger.info(f"{self.agent_context.request_id} code_interpreter recv data: {data}")
                            code_response = CodeInterpreterResponse.parse_raw(data)
                            
                            if code_response.file_info:
                                for file_info in code_response.file_info:
                                    file = File(
                                        file_name=file_info.file_name,
                                        oss_url=file_info.oss_url,
                                        domain_url=file_info.domain_url,
                                        file_size=file_info.file_size,
                                        description=file_info.file_name,  # fileName用作描述
                                        is_internal_file=False
                                    )
                                    self.agent_context.product_files.append(file)
                                    self.agent_context.task_product_files.append(file)
                            
                            digital_employee = self.agent_context.tool_collection.get_digital_employee(self.get_name())
                            logger.info(f"requestId:{self.agent_context.request_id} task:{self.agent_context.tool_collection.current_task} toolName:{self.get_name()} digitalEmployee:{digital_employee}")
                            self.agent_context.printer.send("code", code_response, digital_employee)
                    
                    # 构建输出内容
                    output_parts = [code_response.code_output]
                    if code_response.file_info:
                        output_parts.append("\n\n其中保存了文件: ")
                        for file_info in code_response.file_info:
                            output_parts.append(f"{file_info.file_name}\n")
                    
                    return "".join(output_parts)
                    
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} code_interpreter request error", exc_info=e)
            raise
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context