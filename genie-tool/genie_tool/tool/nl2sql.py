# -*- coding: utf-8 -*-
# =====================
# 
# 
# Author: liuwen.92
# Date:   2025/09/12
# =====================
import json
import os
from jinja2 import Template
import asyncio
from loguru import logger
from typing import Dict, List
from genie_tool.model.protocal import NL2SQLRequest
from genie_tool.util.prompt_util import get_prompt
from genie_tool.util.llm_util import ask_llm
from genie_tool.util.log_util import timer
from genie_tool.tool.table_rag.table_column_filter import ColumnFilterModule


class NL2SQLAgent:
    def __init__(self, queue: asyncio.Queue=None):
        # 用作流式
        self.queue = queue or asyncio.Queue()
        self.nl2sql_llm_name = os.getenv("NL2SQL_MODEL_NAME")
        self.rewrite_llm_name = os.getenv("REWRITE_MODEL_NAME")
        self.think_llm_name = os.getenv("THINK_MODEL_NAME")
        self.default_model: str = "gpt-4.1"
        self.temperature: float = 0.0
        self.top_p: float = 1.0

    @timer(key="rewrite_query")
    async def _text_to_rewrite(self, request_id,
        query: str,
        model: str,
        temperature: float,
        top_p: float
    ) -> str:
        """
        重写用户查询（非流式）
        将用户的原始查询优化为更清晰、更适合后续处理的表达方式
        """
        prompt_template = Template(get_prompt("nl2sql")["rewrite_prompt"])
        prompt = prompt_template.render(
            query=query
        )
        logger.info(f"[NL2SQL] [REWRITE] request_id={request_id} {prompt=}")
        logger.info(f"[NL2SQL] [REWRITE] request_id={request_id} rewrite模块执行完成。 model_name={model}")
        rewrite_llm_result = ""
        async for chunk in ask_llm(
            messages=prompt,
            model=model,
            stream=False,
            temperature=temperature,
            top_p=top_p,
            only_content=True
        ):
            rewrite_llm_result = chunk
        logger.info(f"[NL2SQL] [REWRITE] request_id={request_id} {rewrite_llm_result=}")
        return rewrite_llm_result

    @timer(key="think")
    async def _collect_think_results(self, request_id,
        query: str,
        # user_info: str,
        current_date_info: str,
        m_schema_formatted: str,
        model: str,
        temperature: float,
        top_p: float
    ) -> str:
        """收集think的完整结果"""
        response = {
                    "code": 200,
                    "err_msg": "",
                    "status": "",
                    "nl2sql_think": "",
                    "data": [],
                    "request_id": ""
                    }
        think_full = ""
        prompt_template = Template(get_prompt("nl2sql")["think_prompt"])
        prompt = prompt_template.render(
            query=query,
            column_info="",
            m_schema_formatted=m_schema_formatted,
            current_date_info=current_date_info
        )
        logger.info(f"[NL2SQL] [THINK] request_id={request_id} {prompt=}")
        async for chunk in ask_llm(
            messages=prompt,
            model=model,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            only_content=False
        ):
            chunk_content = chunk.choices[0].delta.content
            if chunk_content is None or chunk_content == "":
                continue
            think_full += chunk_content
            response["nl2sql_think"] = think_full
            response["status"] = "nl2sql_think"
            await self.queue.put(json.dumps(response, ensure_ascii=False))
        # 思考模型结束标识
        final_response = {
                "code": 200,
                "err_msg": "",
                "status": "finished_stream",
                "nl2sql_think": "",
                "data": [],
                "request_id": request_id
            }
        await self.queue.put(json.dumps(final_response, ensure_ascii=False))
        logger.info(f"[NL2SQL] [THINK] request_id={request_id} think模块执行完成。 model_name={model}")
        logger.info(f"[NL2SQL] [THINK] request_id={request_id} final_response={json.dumps(final_response, ensure_ascii=False)}")
        return response["nl2sql_think"]
    
    def m_schema_trans(self,
                       table_id: str,
                       column_schema_lists: List[Dict],
                       business_prompt: str,
                       time_prompt: str,
                       use_prompt: str,
                       **kwargs
                       ) -> str:
        output = [f"\n## 数据表：{table_id}\n如果要使用当前的数据表，只能使用以下的字段，禁止使用其他数据表的字段。该表字段信息的详细描述："]
        field_lines = []
        for column_schema_info in column_schema_lists:
            field_line = []
            field_type = column_schema_info.get('dataType', "")
            raw_type = field_type
            field_id = column_schema_info["columnId"]
            field_name = column_schema_info.get("columnName", "")
            field_comment = column_schema_info.get("columnComment", "")
            alias_name = column_schema_info.get("synonyms", "")
            few_shot = column_schema_info.get("fewShot", "")
            if field_id != "" and field_id != " ":
                field_line.append(f"字段ID：{field_id}")
            if field_name != "" and field_name != " ":
                field_line.append(f"- 字段名称：{field_name}")
            if raw_type != "" and raw_type != " ":
                field_line.append(f"- 字段类型：{raw_type}")
            if field_comment != "" and field_comment != "":
                field_line.append(f"- 字段描述：{field_comment}")
            if alias_name != "" and alias_name != "":
                field_line.append(f"- 字段别名：{alias_name}")
            if few_shot != "" and few_shot != " ":
                field_line.append(f"- 字段举例：{few_shot}")
            field_lines.append("\n".join(field_line))
        output.append('\n\n'.join(field_lines))
        if business_prompt and len(business_prompt)>0:
            output.append(f"### 业务规则：\n{business_prompt}")
        if time_prompt and len(time_prompt)>0:
            output.append(f"### 时间规则：\n{time_prompt}")
        if use_prompt and len(use_prompt)>0:
            output.append(f"### 数据表使用规范：\n{use_prompt}")
        m_schema_result = '\n'.join(output)
        return m_schema_result

    @timer(key="nl2sql_convert")
    async def _nl2sql_convert(self, request_id,
                              rewritten_query: str,
                              thinking_result: str,
                              current_date_info: str,
                              m_schema_formatted: str,
                              model: str,
                              temperature: float,  # nl2sql使用较低温度保证结果的稳定性
                              top_p: float,
                              dialect: str
    ) -> Dict:
        """
        将查询转换为SQL（非流式）
        结合rewrite和think的结果，生成对应的SQL查询
        """
        prompt_template = Template(get_prompt("nl2sql")["nl2sql_prompt"])
        prompt = prompt_template.render(
            rewritten_query=rewritten_query,
            thinking_result=thinking_result,
            query=rewritten_query,
            m_schema_formatted=m_schema_formatted,
            current_date_info=current_date_info,
            dialect=dialect
        )
        nl2sql_response = ""
        logger.info(f"[NL2SQL] [nl2sql_convert] {request_id=} {prompt=}")
        async for chunk in ask_llm(
                                messages=prompt,
                                model=model,
                                stream=False,
                                temperature=temperature,
                                top_p=top_p,
                                only_content=True
                            ):
            nl2sql_response = chunk
        logger.info(f"[NL2SQL] [nl2sql_convert] {request_id=} {nl2sql_response=}")
        llm_post_result =[]
        if nl2sql_response == "{}":
            return {}
        if nl2sql_response != "":
                    llm_info_list = nl2sql_response.split("@@@")
                    for llm_info in llm_info_list:
                        tmp_dict = {}
                        query_info_list = llm_info.split("###")
                        if len(query_info_list) == 2:
                            tmp_dict["query"] = query_info_list[0]
                            nl2sql = query_info_list[1]
                            nl2sql = nl2sql.replace(";", "")
                            tmp_dict["nl2sql"] = nl2sql
                        if len(tmp_dict) > 0:
                            llm_post_result.append(tmp_dict)
        response = {
            "code": 200,
            "data": llm_post_result,
            "request_id": request_id,
            "status": "data",
            "error_msg": ""
        }
        await self.queue.put(json.dumps(response, ensure_ascii=False))
        final_response = {
                            "code": 200,
                            "err_msg": "",
                            "status": "finished",
                            "nl2sql_think": "",
                            "data": [
                            ],
                            "request_id": "request_id"
                            }
        await self.queue.put(json.dumps(final_response, ensure_ascii=False))
        logger.info(f"[NL2SQL] request_id={request_id} nl2sql模块执行完成。 model_name={model}")
        logger.info(f"[NL2SQL] request_id={request_id} response={json.dumps(response, ensure_ascii=False)}")
        return response
    
    async def m_schema_format(self, rank_result: List):
        m_schema_info = []
        # 并行处理表结构转换
        m_schema_results = [
            self.m_schema_trans(
                table_id=table_schema_info.get("modelCode", ""),
                column_schema_lists=table_schema_info.get("schemaList", []),
                business_prompt=table_schema_info.get("businessPrompt", ""),
                time_prompt=table_schema_info.get("timePrompt", ""),
                use_prompt=table_schema_info.get("usePrompt", "")
            )
            for table_schema_info in rank_result
        ]
        m_schema_info.append("\n".join(m_schema_results))
        return "\n".join(m_schema_info)

    @timer(key="run_nl2sql")
    async def run(self,
                  body: NL2SQLRequest,
                  **kwargs) -> Dict:
        request_id = body.request_id
        logger.info(f"[NL2SQL] [REQUEST], request_body={json.dumps(body.model_dump(), ensure_ascii=False)}")
        query = body.query
        current_date_info = body.current_date_info
        table_id_list = body.table_id_list
        column_info = body.column_info
        dialect = body.dialect
        try:
            logger.info(f"[NL2SQL] request_id={request_id}, {query=}")
            # 精排任务：rank
            rank_module = ColumnFilterModule(request_id=request_id,
                                             query=query, 
                                             current_date_info=current_date_info, 
                                             table_id_list=table_id_list, 
                                             column_info=column_info)
            rank_task = asyncio.create_task(rank_module.batch_get_result())
            # 改写任务：rewrite
            rewrite_task = asyncio.create_task(
                self._text_to_rewrite(request_id=request_id,
                                      query=query, 
                                      model=self.default_model if self.rewrite_llm_name == "" else self.rewrite_llm_name,
                                      temperature=self.temperature,
                                      top_p=self.top_p)
            )
            # 并发执行rank和rewrite，等待完成
            rewritten_query, rank_result = await asyncio.gather(rewrite_task, rank_task)
            m_schema_formatted = await self.m_schema_format(rank_result)

            # 处理think的流式输出并同时收集完整结果
            full_thinking = await self._collect_think_results(request_id=request_id,
                                            query=query,
                                            current_date_info=current_date_info, 
                                            m_schema_formatted=m_schema_formatted, 
                                            model=self.default_model if self.think_llm_name == "" else self.think_llm_name,
                                            temperature=self.temperature,
                                            top_p=self.top_p)
            # SQL 生成器
            nl2sql_response = await self._nl2sql_convert(request_id=request_id,
                                                         rewritten_query=rewritten_query,
                                                         thinking_result=full_thinking,
                                                         current_date_info=current_date_info, 
                                                         m_schema_formatted=m_schema_formatted, 
                                                         model=self.default_model if self.nl2sql_llm_name == "" else self.nl2sql_llm_name,
                                                         temperature=self.temperature,
                                                         top_p=self.top_p,
                                                         dialect=dialect)
            logger.info(f"[NL2SQL] [run_nl2sql], nl2sql_response={json.dumps(nl2sql_response, ensure_ascii=False)}")
            return nl2sql_response
        except Exception as e:
            err_response = {"code": 6001, "data": "", "request_id": "request_id", "err_msg": e, "status": "data"}
            await self.queue.put(json.dumps(err_response, ensure_ascii=False))
            logger.error(f"[NL2SQL] request_id={request_id} NL2SQL模块执行失败！！！ {e}")
            return err_response
        finally:
            await self.queue.put("[DONE]")

