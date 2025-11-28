# -*- coding: utf-8 -*-
# =====================
# 
# 
# Author: liumin.423
# Date:   2025/7/7
# =====================
import hashlib
from typing import Optional, Literal, List

from pydantic import BaseModel, Field, computed_field


class StreamMode(BaseModel):
    """流式模式
    args:
        mode: 流式模式 general 普通流式 token 按token流式 time 按时间流式
        token: 流式模式下，每多少个token输出一次
        time: 流式模式下，每多少秒输出一次
    """
    mode: Literal["general", "token", "time"] = Field(default="general")
    token: Optional[int] = Field(default=5, ge=1)
    time: Optional[int] = Field(default=5, ge=1)


class CIRequest(BaseModel):
    request_id: str = Field(alias="requestId", description="Request ID")
    task: Optional[str] = Field(default=None, description="Task")
    file_names: Optional[List[str]] = Field(default=[], alias="fileNames", description="输入的文件列表")
    file_name: Optional[str] = Field(default=None, alias="fileName", description="返回的生成的文件名称")
    file_description: Optional[str] = Field(default=None, alias="fileDescription", description="返回的生成的文件描述")
    stream: bool = True
    stream_mode: Optional[StreamMode] = Field(default=StreamMode(), alias="streamMode", description="流式模式")
    origin_file_names: Optional[List[dict]] = Field(default=None, alias="originFileNames", description="原始文本信息")


class ReportRequest(CIRequest):
    file_type: Literal["html", "markdown", "ppt"] = Field("html", alias="fileType", description="生成报告的文件类型")


class FileRequest(BaseModel):
    request_id: str = Field(alias="requestId", description="Request ID")
    file_name: str = Field(alias="fileName", description="文件名称")

    @computed_field
    def file_id(self) -> str:
        return get_file_id(self.request_id, self.file_name)


def get_file_id(request_id: str, file_name: str) -> str:
    return hashlib.md5((request_id + file_name).encode("utf-8")).hexdigest()


class FileListRequest(BaseModel):
    request_id: str = Field(alias="requestId", description="Request ID")
    filters: Optional[List[FileRequest]] = Field(default=None, description="过滤条件")
    page: int = 1
    page_size: int = Field(default=10, alias="pageSize", description="Request ID")


class FileUploadRequest(FileRequest):
    description: str = Field(description="返回的生成的文件描述")
    content: str = Field(description="返回的生成的文件内容")


class DeepSearchRequest(BaseModel):
    request_id: str = Field(description="Request ID")
    query: str = Field(description="搜索查询")
    max_loop: Optional[int] = Field(default=1, description="最大循环次数")

    # bing, jina, sogou
    search_engines: List[str] = Field(default=[], description="使用哪些搜索引擎")

    stream: bool = Field(default=True, description="是否流式响应")
    stream_mode: Optional[StreamMode] = Field(default=StreamMode(), alias="streamMode", description="流式模式")
