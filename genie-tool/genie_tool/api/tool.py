# -*- coding: utf-8 -*-
# =====================
#
#
# Author: liumin.423
# Date:   2025/7/7
# =====================
import asyncio
import contextvars
import json
import os
import threading
import time

from dotenv import load_dotenv
from fastapi import APIRouter
from jinja2 import Template
from sse_starlette import ServerSentEvent, EventSourceResponse

from genie_tool.model.code import ActionOutput, CodeOuput
from genie_tool.model.protocal import TableRAGRequest, AutoAnalysisRequest, CIRequest, CalEngineRequest, ReportRequest, \
    DeepSearchRequest, NL2SQLRequest, SopChooseRequest, MultimodalRAGRequest
from genie_tool.tool.mrag.query import AgenticRAG
from genie_tool.util.file_util import upload_file
from genie_tool.util.llm_util import ask_llm
from genie_tool.util.prompt_util import get_prompt
from genie_tool.tool.report import report
from genie_tool.tool.code_interpreter import code_interpreter_agent
from genie_tool.util.middleware_util import RequestHandlerRoute
from genie_tool.tool.deepsearch import DeepSearch
from genie_tool.tool.auto_analysis import AutoAnalysisAgent
from genie_tool.tool.nl2sql import NL2SQLAgent
from genie_tool.tool.table_rag import TableRAGAgent
from genie_tool.tool.plan_sop import PlanSOP
from genie_tool.util.log_util import logger
load_dotenv()



router = APIRouter(route_class=RequestHandlerRoute)


@router.post("/code_interpreter")
async def post_code_interpreter(
    body: CIRequest,
):
     # 处理文件路径
    if body.file_names:
        for idx, f_name in enumerate(body.file_names):
            if not f_name.startswith("/") and not f_name.startswith("http"):
                body.file_names[idx] = f"{os.getenv('FILE_SERVER_URL')}/preview/{body.request_id}/{f_name}"

    async def _stream():
        acc_content = ""
        acc_token = 0
        acc_time = time.time()
        async for chunk in code_interpreter_agent(
            task=body.task,
            file_names=body.file_names,
            request_id=body.request_id,
            stream=True,
        ):


            if isinstance(chunk, CodeOuput):
                yield ServerSentEvent(
                    data=json.dumps(
                        {
                            "requestId": body.request_id,
                            "code": chunk.code,
                            "fileInfo": chunk.file_list,
                            "isFinal": False,
                        },
                        ensure_ascii=False,
                    )
                )
            elif isinstance(chunk, ActionOutput):
                yield ServerSentEvent(
                    data=json.dumps(
                        {
                            "requestId": body.request_id,
                            "codeOutput": chunk.content,
                            "fileInfo": chunk.file_list,
                            "isFinal": True,
                        },
                        ensure_ascii=False,
                    )
                )
                yield ServerSentEvent(data="[DONE]")
            else:
                acc_content += chunk
                acc_token += 1
                if body.stream_mode.mode == "general":
                    yield ServerSentEvent(
                        data=json.dumps(
                            {"requestId": body.request_id, "data": chunk, "isFinal": False},
                            ensure_ascii=False,
                        )
                    )
                elif body.stream_mode.mode == "token":
                    if acc_token >= body.stream_mode.token:
                        yield ServerSentEvent(
                            data=json.dumps(
                                {
                                    "requestId": body.request_id,
                                    "data": acc_content,
                                    "isFinal": False,
                                },
                                ensure_ascii=False,
                            )
                        )
                        acc_token = 0
                        acc_content = ""
                elif body.stream_mode.mode == "time":
                    if time.time() - acc_time > body.stream_mode.time:
                        yield ServerSentEvent(
                            data=json.dumps(
                                {
                                    "requestId": body.request_id,
                                    "data": acc_content,
                                    "isFinal": False,
                                },
                                ensure_ascii=False,
                            )
                        )
                        acc_time = time.time()
                        acc_content = ""
                if body.stream_mode.mode in ["time", "token"] and acc_content:
                    yield ServerSentEvent(
                        data=json.dumps(
                            {
                                "requestId": body.request_id,
                                "data": acc_content,
                                "isFinal": False,
                            },
                            ensure_ascii=False,
                        )
                    )
            

    if body.stream:
        return EventSourceResponse(
            _stream(),
            ping_message_factory=lambda: ServerSentEvent(data="heartbeat"),
            ping=15,
        )
    else:
        content = ""
        async for chunk in code_interpreter_agent(
            task=body.task,
            file_names=body.file_names,
            stream=body.stream,
        ):
            content += chunk
        file_info = [
            await upload_file(
                content=content,
                file_name=body.file_name,
                request_id=body.request_id,
                file_type="html" if body.file_type == "ppt" else body.file_type,
            )
        ]
        return {
            "code": 200,
            "data": content,
            "fileInfo": file_info,
            "requestId": body.request_id,
        }


@router.post("/report")
async def post_report(
    body: ReportRequest,
):
    # 处理文件路径
    if body.file_names:
        for idx, f_name in enumerate(body.file_names):
            if not f_name.startswith("/") and not f_name.startswith("http"):
                body.file_names[idx] = f"{os.getenv('FILE_SERVER_URL')}/preview/{body.request_id}/{f_name}"
    
    def _parser_html_content(content: str):
        if content.startswith("```\nhtml"):
            content = content[len("```\nhtml"): ]
        if content.startswith("```html"):
            content = content[len("```html"): ]
        if content.endswith("```"):
            content = content[: -3]
        return content

    async def _stream():
        content = ""
        acc_content = ""
        acc_token = 0
        acc_time = time.time()
        async for chunk in report(
            task=body.task,
            file_names=body.file_names,
            file_type=body.file_type,
            template_type=body.template_type,
        ):
            content += chunk
            acc_content += chunk
            acc_token += 1
            if body.stream_mode.mode == "general":
                yield ServerSentEvent(
                    data=json.dumps(
                        {"requestId": body.request_id, "data": chunk, "isFinal": False},
                        ensure_ascii=False,
                    )
                )
            elif body.stream_mode.mode == "token":
                if acc_token >= body.stream_mode.token:
                    yield ServerSentEvent(
                        data=json.dumps(
                            {
                                "requestId": body.request_id,
                                "data": acc_content,
                                "isFinal": False,
                            },
                            ensure_ascii=False,
                        )
                    )
                    acc_token = 0
                    acc_content = ""
            elif body.stream_mode.mode == "time":
                if time.time() - acc_time > body.stream_mode.time:
                    yield ServerSentEvent(
                        data=json.dumps(
                            {
                                "requestId": body.request_id,
                                "data": acc_content,
                                "isFinal": False,
                            },
                            ensure_ascii=False,
                        )
                    )
                    acc_time = time.time()
                    acc_content = ""
        if body.stream_mode.mode in ["time", "token"] and acc_content:
            yield ServerSentEvent(
                data=json.dumps({"requestId": body.request_id, "data": acc_content, "isFinal": False},
                                ensure_ascii=False))
        if body.file_type in ["ppt", "html"]:
            content = _parser_html_content(content)
        file_info = [await upload_file(content=content, file_name=body.file_name, request_id=body.request_id,
                                 file_type="html" if body.file_type == "ppt" else body.file_type)]
        yield ServerSentEvent(data=json.dumps(
            {"requestId": body.request_id, "data": content, "fileInfo": file_info,
             "isFinal": True}, ensure_ascii=False))
        yield ServerSentEvent(data="[DONE]")

    if body.stream:
        return EventSourceResponse(
            _stream(),
            ping_message_factory=lambda: ServerSentEvent(data="heartbeat"),
            ping=15,
        )
    else:
        content = ""
        async for chunk in report(
            task=body.task,
            file_names=body.file_names,
            file_type=body.file_type,
            template_type=body.template_type,
        ):
            content += chunk
        if body.file_type in ["ppt", "html"]:
            content = _parser_html_content(content)
        file_info = [await upload_file(content=content, file_name=body.file_name, request_id=body.request_id,
                                 file_type="html" if body.file_type == "ppt" else body.file_type)]
        return {"code": 200, "data": content, "fileInfo": file_info, "requestId": body.request_id}


@router.post("/deepsearch")
async def post_deepsearch(
    body: DeepSearchRequest,
):
    """深度搜索端点"""
    deepsearch = DeepSearch(engines=body.search_engines)
    async def _stream():
        async for chunk in deepsearch.run(
                query=body.query,
                request_id=body.request_id,
                max_loop=body.max_loop,
                stream=True,
                stream_mode=body.stream_mode,
        ):
            yield ServerSentEvent(data=chunk)
        yield ServerSentEvent(data="[DONE]")

    return EventSourceResponse(_stream(), ping_message_factory=lambda: ServerSentEvent(data="heartbeat"), ping=15)


@router.post("/table_rag")
async def post_table_rag(
    body: TableRAGRequest,
):
    request_id = body.request_id
    query = body.query
    modelCodeList = body.model_code_list
    current_date_info = body.current_date_info
    schema_info = body.schema_info
    recall_type = body.recall_type
    use_vector = body.use_vector
    use_elastic = body.use_elastic
    
    table_rag = TableRAGAgent(request_id=request_id,
                              query=query,
                              modelCodeList=modelCodeList,
                              current_date_info=current_date_info,
                              schema_info=schema_info,
                              user_info="",
                              use_vector=use_vector,
                              use_elastic=use_elastic,)
    
    if recall_type == "only_recall":
        result = await table_rag.run_recall(query=query)
    else:
        
        result = await table_rag.run(query=query)
    content = result.get("choosed_schema", {})
    return {"code": 200, "data": content, "requestId": body.request_id}


@router.post("/cal_engine")
async def cal_engine(body: CalEngineRequest):
    """根据用户获取数据和用户 query 生成指标计算公式"""
    prompt = Template(get_prompt("analysis")["cal_engine_prompt"]).render(
        query=body.query,
        data=body.data,
    )

    async for chunk in ask_llm(messages=prompt, model=os.getenv("CAL_ENGINE_MODEL", "gpt-4.1"), only_content=True):
        expression = chunk
    return {"code": 200, "expression": expression, "request_id": body.request_id, "query": body.query}


@router.post("/auto_analysis")
async def auto_analysis(body: AutoAnalysisRequest):
    if body.stream:
        queue = asyncio.Queue()
        async def _stream(queue):
            if not body.modelCodeList:
                yield ServerSentEvent(data="没有提供数据源，无法进行数据分析")
            else:
                while True:
                    data = await queue.get()
                    if data == "[DONE]":
                        yield ServerSentEvent(data=data)
                        break
                    if not isinstance(data, str):
                        data = json.dumps(data, ensure_ascii=False)
                    yield ServerSentEvent(data=data)
        
        def run_task(context, queue, body):
            if body.modelCodeList:
                context.run(lambda : asyncio.run(AutoAnalysisAgent(queue=queue, max_steps=body.max_steps, stream=body.stream).run(**body.model_dump())))
            
        thread = threading.Thread(target=run_task, args=(contextvars.copy_context(), queue, body), daemon=True)
        thread.start()
        return EventSourceResponse(
            _stream(queue),
            ping_message_factory=lambda: ServerSentEvent(data="heartbeat"),
            ping=15,
        )
    else:
        response = {"code": 200, "data": {}, "request_id": body.request_id}
        if not body.modelCodeList:
            response["data"] = "没有提供数据源，无法进行数据分析"
        else:
            response["data"] = await AutoAnalysisAgent(max_steps=body.max_steps).run(**body.model_dump())
        return response


@router.post("/nl2sql")
async def post_nl2sql(body: NL2SQLRequest):
    """
    text_2_sql
    """
    nl2sql_queue = asyncio.Queue()
    if body.stream:
        async def _stream(queue):
            if not body.query:
                yield ServerSentEvent(data="没有提供用户问题，无法进行nl2sql的执行")
            else:
                while True:
                    data = await queue.get()
                    if data == "[DONE]":
                        yield ServerSentEvent(data=data)
                        break
                    if not isinstance(data, str):
                        data = json.dumps(data, ensure_ascii=False)
                    yield ServerSentEvent(data=data)

        def run_task(context, queue, body:NL2SQLRequest):
            if body.query:
                context.run(lambda : asyncio.run(NL2SQLAgent(queue=queue).run(body)))

        thread = threading.Thread(target=run_task, args=(contextvars.copy_context(), nl2sql_queue, body), daemon=True)
        thread.start()
        return EventSourceResponse(
            _stream(nl2sql_queue),
            ping_message_factory=lambda: ServerSentEvent(data="heartbeat"),
            ping=15,
        )
    else:
        response = {"code": 200, "data": {}, "request_id": body.request_id, "status": "data"}
        if not body.query:
            response["err_msg"] = "没有提供用户问题，无法进行nl2sql的执行"
        else:
            response = await NL2SQLAgent().run(body)
        return response


@router.post("/sopRecall")
async def post_sop_recall(
    body: SopChooseRequest,
):
    request_id = body.request_id
    query = body.query
    sop_list = body.sop_list
    pl_sop = PlanSOP(request_id)
    sop_mode, choosed_sop_string = pl_sop.sop_choose(query=query, sop_list=sop_list)
    
    return {"code": 200, "data": {"sop_mode": sop_mode, "choosed_sop_string": choosed_sop_string}, "requestId": body.request_id}




@router.post("/mragQuery")
async def chat_completion(request: MultimodalRAGRequest):
    """
    处理聊天完成请求
    """
    # 调用LLM模型生成回复
    kb_id = request.kb_id
    if not kb_id:
        kb_id = os.getenv("DEFAULT_KB_ID")

    logger.info(f"kb_id:{kb_id}")
    agent = AgenticRAG(kb_id=kb_id, n_round=3)

    def generator():
        for chunk in agent.run(request.question, request.image_urls):
            yield chunk.model_dump_json()

        yield "[DONE]"

    return EventSourceResponse(generator())
