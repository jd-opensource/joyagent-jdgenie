"""
Report tool for generating HTML and Markdown reports.
报告工具，可以通过编写HTML、MarkDown报告
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
from ...util.string_util import StringUtil

logger = logging.getLogger(__name__)


class ReportTool(BaseTool):
    """Report tool for generating HTML and Markdown reports."""
    
    def __init__(self):
        self.agent_context = None
    
    def get_name(self) -> str:
        return "report_tool"
    
    def get_description(self) -> str:
        desc = "这是一个报告工具，可以通过编写HTML、MarkDown报告"
        config = DependencyContainer.get_config()
        return config.report_tool_desc if config.report_tool_desc else desc
    
    def to_params(self) -> Dict[str, Any]:
        config = DependencyContainer.get_config()
        if config.report_tool_params:
            return config.report_tool_params
        
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
        start_time = asyncio.get_event_loop().time()
        
        try:
            params = input_data if isinstance(input_data, dict) else {}
            task = params.get("task", "")
            file_description = params.get("fileDescription", "")
            file_name = params.get("fileName", "")
            file_type = params.get("fileType", "")
            
            if not file_name:
                err_message = "文件名参数为空，无法生成报告。"
                logger.error(f"{self.agent_context.request_id} {err_message}")
                return None
            
            file_names = [file.file_name for file in self.agent_context.product_files]
            
            stream_mode = {
                "mode": "token",
                "token": 10
            }
            
            request = CodeInterpreterRequest(
                request_id=self.agent_context.session_id,  # 适配多轮对话
                query=self.agent_context.query,
                task=task,
                file_names=file_names,
                file_name=file_name,
                file_description=file_description,
                stream=True,
                content_stream=self.agent_context.is_stream,
                stream_mode=stream_mode,
                file_type=file_type
            )
            
            # 调用流式 API
            return asyncio.run(self._call_code_agent_stream(request))
            
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} report_tool error", exc_info=e)
        return None
    
    async def _call_code_agent_stream(self, code_request: CodeInterpreterRequest) -> str:
        """调用 CodeAgent"""
        try:
            config = DependencyContainer.get_config()
            url = f"{config.code_interpreter_url}/v1/tool/report"
            
            timeout = httpx.Timeout(connect=60.0, read=600.0, write=600.0, pool=600.0)
            
            logger.info(f"{self.agent_context.request_id} report_tool request {json.dumps(code_request.dict())}")
            
            interval = config.message_interval.get("report", "1,4").split(",")
            first_interval = int(interval[0])
            send_interval = int(interval[1])
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=code_request.dict(),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if not response.is_success:
                        logger.error(f"{self.agent_context.request_id} report_tool request error.")
                        raise Exception(f"Unexpected response code: {response.status_code}")
                    
                    logger.info(f"{self.agent_context.request_id} report_tool response {response.status_code}")
                    
                    code_response = CodeInterpreterResponse(
                        code_output="report_tool 执行失败"  # 默认输出
                    )
                    
                    index = 1
                    string_builder_incr = []
                    message_id = StringUtil.get_uuid()
                    # 获取数字人名称
                    digital_employee = self.agent_context.tool_collection.get_digital_employee(self.get_name())
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break
                            if index == 1 or index % 100 == 0:
                                logger.info(f"{self.agent_context.request_id} report_tool recv data: {data}")
                            if data.startswith("heartbeat"):
                                continue
                            
                            code_response = CodeInterpreterResponse.parse_raw(data)
                            
                            if code_response.is_final:
                                # report_tool 只会输出一个文件，使用模型输出的文件名和描述
                                if code_response.file_info:
                                    for file_info in code_response.file_info:
                                        file = File(
                                            file_name=code_request.file_name,
                                            file_size=file_info.file_size,
                                            oss_url=file_info.oss_url,
                                            domain_url=file_info.domain_url,
                                            description=code_request.file_description,
                                            is_internal_file=False
                                        )
                                        self.agent_context.product_files.append(file)
                                        self.agent_context.task_product_files.append(file)
                                
                                self.agent_context.printer.send(message_id, code_request.file_type, code_response, digital_employee, True)
                            else:
                                string_builder_incr.append(code_response.data or "")
                                if index == first_interval or index % send_interval == 0:
                                    code_response.data = "".join(string_builder_incr)
                                    self.agent_context.printer.send(message_id, code_request.file_type, code_response, digital_employee, False)
                                    string_builder_incr.clear()
                            index += 1
                    
                    # 统一使用data字段，兼容历史codeOutput逻辑
                    result = code_response.data if (code_response.data and code_response.data.strip()) else code_response.code_output
                    return result
                    
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} report_tool request error", exc_info=e)
            raise
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context