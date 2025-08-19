"""
File tool for uploading and downloading files.
文件工具，可以上传或下载文件
"""
import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from ..base_tool import BaseTool
from ...dto.code_interpreter_response import CodeInterpreterResponse
from ...dto.file import File
from ...dto.file_request import FileRequest
from ...dto.file_response import FileResponse
from ...util.dependency_container import DependencyContainer
from ...util.string_util import StringUtil

logger = logging.getLogger(__name__)


class FileTool(BaseTool):
    """File tool for uploading and downloading files."""
    
    def __init__(self):
        self.agent_context = None
    
    def get_name(self) -> str:
        return "file_tool"
    
    def get_description(self) -> str:
        desc = "这是一个文件工具，可以上传或下载文件"
        config = DependencyContainer.get_config()
        return config.file_tool_desc if config.file_tool_desc else desc
    
    def to_params(self) -> Dict[str, Any]:
        config = DependencyContainer.get_config()
        if config.file_tool_params:
            return config.file_tool_params
        
        command = {
            "type": "string",
            "description": "文件操作类型：upload、get"
        }
        
        file_name = {
            "type": "string",
            "description": "文件名"
        }
        
        file_desc = {
            "type": "string", 
            "description": "文件描述，20字左右，upload时必填"
        }
        
        file_content = {
            "type": "string",
            "description": "文件内容，upload时必填"
        }
        
        parameters = {
            "type": "object",
            "properties": {
                "command": command,
                "filename": file_name,
                "description": file_desc,
                "content": file_content
            },
            "required": ["command", "filename"]
        }
        
        return parameters
    
    def execute(self, input_data: Any) -> Any:
        try:
            params = input_data if isinstance(input_data, dict) else {}
            command = params.get("command", "")
            file_request = FileRequest.parse_obj(input_data)
            file_request.request_id = self.agent_context.request_id
            
            if command == "upload":
                return self.upload_file(file_request, True, False)
            elif command == "get":
                return self.get_file(file_request, True)
                
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} file tool error", exc_info=e)
        return None
    
    def upload_file(self, file_request: FileRequest, is_notice_fe: bool, is_internal_file: bool) -> Optional[str]:
        """上传文件的 API 请求方法"""
        try:
            config = DependencyContainer.get_config()
            url = f"{config.code_interpreter_url}/v1/file_tool/upload_file"
            
            # 构建请求体 多轮对话替换requestId为sessionId
            file_request.request_id = self.agent_context.session_id
            # 清理文件名中的特殊字符
            file_request.file_name = StringUtil.remove_special_chars(file_request.file_name)
            
            if not file_request.file_name:
                error_message = "上传文件失败 文件名为空"
                logger.error(f"{self.agent_context.request_id} {error_message}")
                return None
            
            timeout = httpx.Timeout(connect=60.0, read=300.0, write=300.0, pool=300.0)
            
            logger.info(f"{self.agent_context.request_id} file tool upload request {json.dumps(file_request.dict())}")
            
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    url,
                    json=file_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if not response.is_success or not response.content:
                    logger.error(f"{self.agent_context.request_id} upload file failed")
                    return None
                
                result = response.text
                file_response = FileResponse.parse_raw(result)
                logger.info(f"{self.agent_context.request_id} file tool upload response {result}")
                
                # 构建前端格式
                result_map = {
                    "command": "写入文件",
                    "fileInfo": [
                        {
                            "fileName": file_request.file_name,
                            "ossUrl": file_response.oss_url,
                            "domainUrl": file_response.domain_url,
                            "fileSize": file_response.file_size
                        }
                    ]
                }
                
                # 获取数字人
                digital_employee = self.agent_context.tool_collection.get_digital_employee(self.get_name())
                logger.info(f"requestId:{self.agent_context.request_id} task:{self.agent_context.tool_collection.current_task} toolName:{self.get_name()} digitalEmployee:{digital_employee}")
                
                # 添加文件到上下文
                file = File(
                    oss_url=file_response.oss_url,
                    domain_url=file_response.domain_url,
                    file_name=file_request.file_name,
                    file_size=file_response.file_size,
                    description=file_request.description,
                    is_internal_file=is_internal_file
                )
                self.agent_context.product_files.append(file)
                
                if is_notice_fe:
                    # 内部文件不通知前端
                    self.agent_context.printer.send("file", result_map, digital_employee)
                
                if not is_internal_file:
                    # 非内部文件，参与交付物
                    self.agent_context.task_product_files.append(file)
                
                # 返回工具执行结果
                return f"{file_request.file_name} 写入到文件链接: {file_response.oss_url}"
                
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} upload file error", exc_info=e)
        return None
    
    def get_file(self, file_request: FileRequest, notice_fe: bool) -> Optional[str]:
        """获取文件的 API 请求方法"""
        try:
            config = DependencyContainer.get_config()
            url = f"{config.code_interpreter_url}/v1/file_tool/get_file"
            
            # 构建请求体
            get_file_request = FileRequest(
                request_id=self.agent_context.session_id,  # 适配多轮对话
                file_name=file_request.file_name
            )
            
            timeout = httpx.Timeout(connect=60.0, read=300.0, write=300.0, pool=300.0)
            
            logger.info(f"{self.agent_context.request_id} file tool get request {json.dumps(get_file_request.dict())}")
            
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    url,
                    json=get_file_request.dict(),
                    headers={"Content-Type": "application/json"}
                )
                
                if not response.is_success or not response.content:
                    err_message = f"获取文件失败 {file_request.file_name}"
                    return err_message
                
                result = response.text
                file_response = FileResponse.parse_raw(result)
                logger.info(f"{self.agent_context.request_id} file tool get response {result}")
                
                # 构建前端格式
                result_map = {
                    "command": "读取文件",
                    "fileInfo": [
                        {
                            "fileName": file_request.file_name,
                            "ossUrl": file_response.oss_url,
                            "domainUrl": file_response.domain_url,
                            "fileSize": file_response.file_size
                        }
                    ]
                }
                
                # 获取数字人
                digital_employee = self.agent_context.tool_collection.get_digital_employee(self.get_name())
                logger.info(f"requestId:{self.agent_context.request_id} task:{self.agent_context.tool_collection.current_task} toolName:{self.get_name()} digitalEmployee:{digital_employee}")
                
                # 通知前端
                if notice_fe:
                    self.agent_context.printer.send("file", result_map, digital_employee)
                
                # 返回工具执行结果
                file_content = self._get_url_content(file_response.oss_url)
                if file_content is not None:
                    if len(file_content) > config.file_tool_content_truncate_len:
                        file_content = file_content[:config.file_tool_content_truncate_len]
                    
                    return f"文件内容 {file_content}"
                    
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} get file error", exc_info=e)
        return None
    
    def _get_url_content(self, url: str) -> Optional[str]:
        """获取URL内容"""
        try:
            timeout = httpx.Timeout(connect=60.0, read=60.0, write=60.0, pool=60.0)
            
            with httpx.Client(timeout=timeout) as client:
                response = client.get(url)
                
                if response.is_success and response.content:
                    return response.text
                else:
                    logger.error(f"{self.agent_context.request_id} 获取文件失败 {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"{self.agent_context.request_id} 获取文件异常", exc_info=e)
            return None
    
    def set_agent_context(self, agent_context):
        """Set the agent context."""
        self.agent_context = agent_context