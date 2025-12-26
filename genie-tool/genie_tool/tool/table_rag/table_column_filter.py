
import re
import os
import asyncio
import json
import textwrap
import time
import traceback
import json_repair

from calendar import day_name
from datetime import date

from typing import List, Dict
from jinja2 import Template

from genie_tool.util.prompt_util import get_prompt
from genie_tool.util.log_util import logger
from genie_tool.util.llm_util import ask_llm
from genie_tool.tool.table_rag.utils import read_json

class ColumnFilterModule:
    
    # def __init__(self, request_body: dict[str, dict[str]]):
    def __init__(self,
                 request_id: str,
                 query: str,
                current_date_info: str,
                table_id_list: List[str],
                column_info: List[Dict],
                 ):
        
        self.llm_model_name = os.getenv("TR_TABLE_FILTER_MODEL_NAME")
        self.table_filter_model_name = os.getenv("TR_COLUMN_FILTER_MODEL_NAME")
        
        self._is_first_filter_table = os.getenv("TR_IS_FIRST_FILTER_TABLE", True)
        self.need_filter_table_min_length = int(os.getenv("TR_NEED_FILTER_TABLE_MIN_LENGTH", 3))
        self.table_filter_batch_size = int(os.getenv("TR_TABLE_FILTER_BATCH_SIZE", 5))
        
        # self.body = request_body
        # self.user_info = request_body.get("user_info", "")
        self.user_info = ""
        # self.memory_info = request_body.get("memory_info", "")
        self.memory_info = []
        self.current_date_info = current_date_info
        self.query = query
        self.request_id = request_id
        self.table_schema_lists = table_id_list
        self.column_info = column_info
        self.schema_list_max_length = int(os.getenv("TR_SCHEMA_LIST_MAX_LENGTH", 200))
        self.business_prompt_max_length = int(os.getenv("TR_BUSINESS_PROMPT_MAX_LENGTH", 3000))
        self.use_prompt_max_length = int(os.getenv("TR_USE_PROMPT_MAX_LENGTH", 500))

    @property
    def time_info(self) -> str:
        # current_date_info = self.body.get("current_date_info", "")
        # current_date_info = self.current_date_info
        today = date.today()
        day_of_week = day_name[today.weekday()]
        if self.current_date_info == "" or self.current_date_info == " ":
            self.current_date_info = f"今天是 {today.strftime('%Y年%m月%d日')}，星期{day_of_week}"
        
        return self.current_date_info
    
    # @property
    # def query_get(self) -> str:
    #     # return self.body.get("query", "")
    #     return self.query
    
    def schema2str(self, schema) -> str:
        columnName = schema.get("columnName", "") or ""
        fewShot = schema.get("fewShot", "") or ""
        synonyms = schema.get("synonyms", "") or ""
        columnComment = schema.get("columnComment", "") or ""
        schema_str = ""
        if columnName:
            schema_str = "字段名：" + columnName
            if columnComment:
                schema_str += "- 解释：" + columnComment
            if synonyms:
                schema_str += "- 近义词有：" + synonyms
            if fewShot:
                schema_str += "- 取值示例：" + fewShot
        
        return schema_str
    
    def schema_list2str(self, schema_list: list[dict]) -> str:
        # {
        #     "projectCode": "onedata",
        #     "analyzeSuggest": 0,
        #     "defaultRecall": 0
        # },
        schema_list_str = ""
        id2schema_map = {}
        for index, schema in enumerate(schema_list):
            columnId = index + 1
            schema_str = self.schema2str(schema)
            schema_list_str += schema_str + "\n"
        
        return schema_list_str
    
    def get_memroy_info_str(self):
        memory_info_str = ""
        for message in self.memory_info:
            role = message.get("role", "")
            content = message.get("content", "")
            status = message.get("status", "")
            if content and status:
                memory_info_str += f"{role}: {content}\n"
        
        return memory_info_str
    
    def _generate_table_filter_prompt(self, table_schema_info_list, error_msg: str | None):
        table_info_list_str = ""
        index2model_code_id_map = {}
        for index, table_schema_info in enumerate(table_schema_info_list):
            tableId = index + 1
            table_name = table_schema_info.get("modelName", "")
            schemaList = table_schema_info.get("schemaList", [])
            # 仅保留部分关键信息用于选表
            # 字段名，字段内容，fewshot，
            schema_list_str = self.schema_list2str(schemaList)[:self.schema_list_max_length]
            businessPrompt = table_schema_info.get("businessPrompt", "")[:self.business_prompt_max_length]
            usePrompt = table_schema_info.get("usePrompt", "")[:self.use_prompt_max_length]
            
            table_info_str = f"""
                                <编号>：{tableId} <编号>
                                <表名>：{table_name}<表名>
                                <表描述>：{businessPrompt}<表描述>
                                <使用说明>：{usePrompt}<使用说明>
                                <表的相关字段>：{schema_list_str}<表的相关字段>
                                """
            table_info_list_str += textwrap.dedent(table_info_str) + "\n\n"
            index2model_code_id_map[tableId] = table_schema_info
        
        memory_info_str = self.get_memroy_info_str()
        model_code_list = [index + 1 for index in range(len(table_schema_info_list))]
        table_info = table_info_list_str.strip()

        table_rag_prompts = get_prompt("table_rag")
        prompt = Template(table_rag_prompts["table_filter_prompt"]) \
            .render(model_code_list=model_code_list,
                    table_info=table_info,
                    user_info=self.user_info,
                    time_info=self.time_info,
                    query=self.query,
                    memory_info=memory_info_str)

        return prompt, index2model_code_id_map
    
    def _generate_filter_prompt(self, table_schema_info: dict, error_msg: str | None):
        
        table_id = table_schema_info.get("modelCode", "")
        table_name = table_schema_info.get("modelName", "")
        columns = table_schema_info.get("schemaList", [])
        
        to_model_columns = []
        keep_keys = ["columnIndex", "columnName", "columnComment", "synonyms", "fewShot", "dataType"]
        no_keys = set()
        for i in range(len(columns)):
            column = columns[i]
            column["columnIndex"] = i + 1
            # 使用浅拷贝 把columnIndex 回传回去了, 因此，去掉大模型不需要的额外信息
            to_model_column = {}
            
            for key in keep_keys:
                if key in column:
                    to_model_column[key] = column[key]
                else:
                    no_keys.add(key)
            
            to_model_columns.append(to_model_column)
        memory_info_str = self.get_memroy_info_str()

        table_info = {
            # "tableId": table_id,
            "tableName": table_name,
            "businessPrompt": table_schema_info.get("businessPrompt", ""),
            "usePrompt": table_schema_info.get("usePrompt", ""),
            "columns": to_model_columns
        }
        
        info_dict = {
            "table_info": table_info,
            "user_info": self.user_info,
            "time_info": self.time_info,
            "query": self.query,
            "memory_info": memory_info_str,
            "error_msg": error_msg
        }
        table_rag_prompts = get_prompt("table_rag")
        prompt = Template(table_rag_prompts["column_filter_prompt"]).render(info_dict)
        
        return prompt
    
    def _parse_json_result(self, result_str):
        pattern = r'```json\s*([\s\S]*?)\s*```'
        try:
            result = re.findall(pattern, result_str)
            return result[0]
        except Exception as e:
            logger.error(f"生成结果格式不合法:{result_str}，{e}")
            raise RuntimeError("解析llm json结果失败")
    
    async def _filter_single_table(self, semaphore, table_schema_info: dict) -> dict | None:
        
        async with semaphore:
            llm_response = ""
            request_id = ""
            error_msg = None
            for retry in range(3):
                try:
                    columns_prompt = self._generate_filter_prompt(table_schema_info, error_msg)
                    
                    messages = [
                        {
                            "role": "system",
                            "content": "you are a helpful assistant.",
                        },
                        {
                            "role": "user",
                            "content": columns_prompt
                        }
                    ]
                    
                    request_id = self.request_id

                    async for chunk in ask_llm(messages=messages,
                                       model=self.llm_model_name,
                                       stream=False,
                                       temperature=0,
                                       top_p=0.95,
                                       only_content=True):
                        llm_response += chunk
                    # result_dict = json.loads(self._parse_json_result(llm_response))
                    result_dict = json_repair.loads(llm_response)
                    if str(result_dict["relatedFlag"]).lower() == "true":
                        columns = table_schema_info.get("schemaList", [])
                        # column_map = {column["columnId"]: column for column in columns}
                        
                        filter_columns = []
                        # result_column_ids = [column["columnId"] for column in result_dict["columns"]]
                        result_column_indexes = result_dict["columnIndexes"]
                        for column_info in columns:
                            # column_id = column_info.get("columnId", "")
                            column_index = column_info.get("columnIndex", "")
                            default_recall = column_info.get("defaultRecall", 0)
                            
                            if column_index in result_column_indexes or default_recall == 1:
                                filter_columns.append(column_info)
                        
                        table_schema_info["schemaList"] = filter_columns
                        return table_schema_info
                    else:
                        return None
                
                except Exception as e:
                    error_msg = f"第{retry + 1}次执行结果:\n{llm_response}，报错信息:{e}"
                    
                    traceback.print_exc()
                    logger.error(f"[filter column] {request_id}, fail to filter columns error_msg {error_msg}")
                    continue
            
            raise RuntimeError(f"[filter column] {request_id} 多次重试后执行失败, error_msg:{error_msg}")
    
    async def batch_get_stage_result(self):
        # table_schema_lists = self.body.get("schema_info", [])
        table_schema_lists = self.column_info
        
        if not table_schema_lists:
            return []
        
        # 第一阶段：批处理过滤（粗筛）
        batch_size = self.table_filter_batch_size  # 增大 batch 提高吞吐
        semaphore1 = asyncio.Semaphore(self.table_filter_batch_size)
        
        # 流式生成 batch
        def batch_generator():
            for i in range(0, len(table_schema_lists), batch_size):
                yield table_schema_lists[i:i + batch_size]
        
        # 异步执行所有 batch，流式获取完成结果
        batch_tasks = [
            asyncio.create_task(self.filter_table(semaphore1, batch))
            for batch in batch_generator()
        ]
        
        # 流式收集第一阶段结果，并立即提交第二阶段
        second_stage_tasks = []
        semaphore2 = asyncio.Semaphore(self.table_filter_batch_size)  # 第二阶段并发控制
        
        # 使用 as_completed 提前处理完成的 batch
        for coro in asyncio.as_completed(batch_tasks):
            try:
                filtered_batch = await coro
                if not filtered_batch:
                    continue
                # 为第二阶段创建单个表的 task，并控制并发
                for item in filtered_batch:
                    task = asyncio.create_task(self._filter_single_table(semaphore2, item))
                    second_stage_tasks.append(task)
            except Exception as e:
                # 可选：记录异常，不影响其他任务
                error_msg = traceback.format_exc().replace("\n", "\\n")
                logger.error(f"Error in first stage batch: {e} error_msg {error_msg}")
                continue
        
        # 等待所有第二阶段任务完成
        if not second_stage_tasks:
            return []
        
        filter_tables = await asyncio.gather(*second_stage_tasks, return_exceptions=True)
        
        # 过滤掉异常（可选）
        results = [r for r in filter_tables if not isinstance(r, Exception)]
        return results
    
    async def filter_table(self, semaphore, schema_info_list):
        async with semaphore:
            if schema_info_list is None or len(schema_info_list) == 0:
                return []
            error_msg = ""
            max_retry = 3
            #
            # request_id = self.body.get("request_id", "")
            request_id = self.request_id
            # llm_erp = self.body.get("erp", "")
            # ducc_config = self.body.get("ducc_config", {}).get("llmconfig", {})
            start_time = time.time()
            
            model_code_list = [table_schema_info.get("modelCode", "") for table_schema_info in schema_info_list]
            logger.info(f"sn: {request_id} Start [filter tables] tables: {model_code_list}")
            prompt, index2model_code_map = self._generate_table_filter_prompt(schema_info_list, error_msg)
            
            messages = [
                {
                    "role": "system",
                    "content": "you are a helpful assistant",
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            llm_response = ""
            async for chunk in ask_llm(messages=messages,
                                       model=self.table_filter_model_name,
                                       stream=False,
                                       temperature=0,
                                       top_p=0.95,
                                       only_content=True):
                llm_response += chunk
                
            end_time = time.time()
            
            logger.info(f"llm_response = {llm_response}")
            
            # index2model_code_map
            llm_response = llm_response[llm_response.find('['):llm_response.find(']') + 1]
            
            # 开始选表
            model_code_index_list = read_json(llm_response)
            schema_info_list = [index2model_code_map[index] for index in model_code_index_list]
            model_code_list = [table_schema_info.get("modelCode", "") for table_schema_info in schema_info_list]
            return schema_info_list
    
    async def batch_get_result(self):
        # table_schema_lists = self.body.get("schema_info", [])
        table_schema_lists = self.column_info
        
        # 不使用2阶段时，直接过滤，以及表长度小于最小并发长度时，直接过滤
        if len(table_schema_lists) < self.need_filter_table_min_length or not self._is_first_filter_table:
            
            semaphore = asyncio.Semaphore(self.table_filter_batch_size)
            filter_tables = await asyncio.gather(
                *[
                    self._filter_single_table(semaphore, item) for item in table_schema_lists
                ]
            )
        
        else:
            filter_tables = await self.batch_get_stage_result()
        
        filter_tables = [table for table in filter_tables if table]
        return filter_tables

async def main():
    body = {
        "currentDateInfo": "当前时间信息：2025-09-12,星期五",
        "dbType": "h2",
        "modelCodeList": [
            "sales",
            "sales_count"
        ],
        "query": "不同国家的数量",
        "recallType": "only_recall",
        "requestId": "b926ea9e-197d-402a-93e9-862b9a2c3725",
        "schemaInfo": [
            {
                "businessPrompt": "业务规则",
                "content": "sales_data",
                "modelCode": "sales",
                "modelName": "超市销售明细数据",
                "schemaList": [
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "国家",
                        "columnId": "COUNTRY",
                        "columnName": "国家",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "中国",
                        "modelCode": "sales",
                        "vectorUuid": "53fa32a4-c839-4981-94ad-460d74728ccb,1bacedaf-186e-474b-8344-b3a4c9eefa8f,cec87836-7705-45ce-a20e-6553cd633854,6b2f6773-b6cb-4162-b49c-947f9191d05e"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "地区",
                        "columnId": "REGION",
                        "columnName": "地区",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "东北,中南,华北,华东,西南,西北",
                        "modelCode": "sales",
                        "vectorUuid": "f7203ac0-fce5-490c-b17d-2e2230cf90ff,6455b1d6-2f88-4b52-a614-7203fa4b3fe7,6c67e82d-1efe-46da-bd84-697cd9677f43,f952cdb5-e378-4856-80c8-ea6871823a78"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "省/自治区",
                        "columnId": "STATE_PROVINCE",
                        "columnName": "省/自治区",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "黑龙江,山东,上海,福建,广东,四川,陕西,河北,浙江,江苏,江西,安徽",
                        "modelCode": "sales",
                        "vectorUuid": "2a87ab71-2ea3-4ac2-8f53-ec66945f6e05,259aceb8-a87b-4dd4-b90c-2596aa672530,1d4ba3f3-4412-42a3-859b-cda194dca1db,2786650a-f6db-4917-b0ff-d5f7fdaf47fb"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "细分",
                        "columnId": "SEGMENT",
                        "columnName": "细分",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "公司,消费者,小型企业",
                        "modelCode": "sales",
                        "vectorUuid": "a24eb206-9810-4143-9b3e-6fcf2d933e8d,38421422-a69c-496f-9792-623bddcb08cb,96217a69-48e4-42a4-82ba-1f6c73ece464,2739a52a-9cda-4724-92fd-70943cc2f950"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "城市",
                        "columnId": "CITY",
                        "columnName": "城市",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "内江,汕头,景德镇,上海,哈尔滨,徐州,温岭,镇江,青岛,唐山,榆林,杭州",
                        "modelCode": "sales",
                        "vectorUuid": "aa3e6492-ad1f-4d89-a4f0-728dcb4374f5,c1d7c4cd-08ac-4ff7-8878-01ea5a6e5577,55e55966-8f99-40ca-a412-cdec8ac53fda,5ab4ce7a-29ac-4d48-bdda-bebeb67dae2d"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "销售数量",
                        "columnId": "QUANTITY",
                        "columnName": "销售数量",
                        "dataType": "DECIMAL",
                        "defaultRecall": 0,
                        "fewShot": "11,1,12,2,3,4,5,6,7,8,9,10",
                        "modelCode": "sales",
                        "vectorUuid": "603d2a85-8472-422c-9b89-4e3ab84eed26,8c510749-58ad-49b7-b480-6d7e0d047335,cca666ee-119d-44ab-8e53-6b08bab61230,164d184b-367d-4d3e-9d98-02ed354e1b23"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "客户名称",
                        "columnId": "CUSTOMER_NAME",
                        "columnName": "客户名称",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "许安,万兰,赵婵,马丽,康青,白鹄,俞明,刘斯云,贾彩,谢雯,曾惠,宋良",
                        "modelCode": "sales",
                        "vectorUuid": "e45340ee-b95f-4649-9e77-93013b674651,93b1a884-010a-4620-848a-3bf8b1700865,964c0836-1ed2-4aaa-aeb0-5d4e75bcce8c,6cb99258-4943-411f-88b3-efb33fbbf196"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "产品名称",
                        "columnId": "PRODUCT_NAME",
                        "columnName": "产品名称",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "Cardinal 孔加固材料, 回收,Kleencut 开信刀, 工业,Green Bar 计划信息表, 多色,柯尼卡 打印机, 红色,爱普生 计算器, 耐用,SAFCO 扶手椅, 可调,惠普 墨水, 红色,KitchenAid 搅拌机, 黑色,Fiskars 剪刀, 蓝色,Stockwell 橡皮筋, 整包,GlobeWeis 搭扣信封, 红色,Ibico 订书机, 实惠",
                        "modelCode": "sales",
                        "vectorUuid": "f5928bae-4310-4862-9f85-58d54cecab2a,257a40a8-3d50-4dcb-9ad1-d968c23373e5,1e7fb9c9-a396-4a83-aa21-cd35d594d3fc,a639e195-8814-4ed0-ab2c-bf6f1ee740dc"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "邮寄方式",
                        "columnId": "SHIP_MODE",
                        "columnName": "邮寄方式",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "二级,标准级,当日,一级",
                        "modelCode": "sales",
                        "vectorUuid": "488995fb-d53c-417a-b4b3-6ea09b6ddfb4,2fe54f00-c2e3-45fa-8600-20511c75bb44,c88937b2-6373-46a5-91b5-f5e9b40faac4,6ad9b26f-5784-463f-8a0c-41eab2f01f41"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "销售额",
                        "columnId": "SALES",
                        "columnName": "销售额",
                        "dataType": "DECIMAL",
                        "defaultRecall": 0,
                        "fewShot": "8659.8400,588.0000,129.6960,321.2160,31.9200,11129.5800,125.4400,1375.9200,2368.8000,434.2800,479.9200,154.2800",
                        "modelCode": "sales",
                        "vectorUuid": "4679f083-50e6-455e-8ff3-d4995f05148e,04017e8c-235f-4a66-8c8c-32ed20514d19,e17a9c08-0da9-4674-b34b-bc50f266a243,01905233-c44d-4758-a988-8f4e53dbf3a3"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "产品类别",
                        "columnId": "CATEGORY",
                        "columnName": "产品类别",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "技术,办公用品,家具",
                        "modelCode": "sales",
                        "vectorUuid": "d9435622-72b8-479e-8219-a5ce9632939e,08cef914-e82a-4dfe-b1d4-623b3ad6d978,d8930b3c-a859-4768-9057-d81497b83b32,765f7371-b7bd-445c-9561-ac8c162fce1b"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "折扣",
                        "columnId": "DISCOUNT",
                        "columnName": "折扣",
                        "dataType": "DECIMAL",
                        "defaultRecall": 0,
                        "fewShot": "0.6000,0.4000,0.2000,0.0000,0.2500,0.1000,0.8000",
                        "modelCode": "sales",
                        "vectorUuid": "016e5558-0a05-48fe-a77e-b3d35c7af235,519e4e65-f313-46f7-a083-53afbe9153df,d77c3e7b-b11a-4344-80da-7523b48c1294,a2d1eed2-d930-4192-b580-72455d317509"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "客户 ID",
                        "columnId": "CUSTOMER_ID",
                        "columnName": "客户 ID",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "康青-19585,白鹄-14050,刘斯-20965,马丽-15910,俞明-18325,谢雯-21700,赵婵-10885,许安-10165,贾彩-10600,宋良-17170,曾惠-14485,万兰-15730",
                        "modelCode": "sales",
                        "vectorUuid": "28179ba9-5139-4d28-b6cf-36f098e29e46,4fa4099c-fb1e-4bd6-88c6-d6d8d2cacc75,922ec908-6c85-4866-b7be-a743680f83b4,6b7502a5-6e05-4b3a-b9f8-ff55e765fda2"
                    }
                ],
                "type": "table",
                "usePrompt": "超市销售明细数据"
            },
            {
                "businessPrompt": "业务规则",
                "content": "select FORMATDATETIME(order_date, 'yyyy') as `订单销售年份` ,FORMATDATETIME(order_date, 'yyyy-MM')  as `订单销售月份` , ship_mode as `邮寄方式`, region as `区域`, state_province as `省份`, category as `产品类型`, sum(sales) as `销售额`,count(quantity) as `销售数量` from sales_data  group by FORMATDATETIME(order_date, 'yyyy'), FORMATDATETIME(order_date, 'yyyy-MM') , ship_mode , region , state_province , category",
                "modelCode": "sales_count",
                "modelName": "超市销售汇总数据",
                "schemaList": [
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "省份",
                        "columnId": "省份",
                        "columnName": "省份",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "山东,黑龙江,吉林,广东,天津,河南,浙江,重庆,广西,湖北,湖南,安徽",
                        "modelCode": "sales_count",
                        "vectorUuid": "c1440cf8-b9ce-4bb5-8e52-eb77d45a4c57,616e302d-6561-49b1-915a-d714bc4ed27b,ecfba984-0f63-4a88-9d1a-1925c4d4327a,d6f504db-4c3d-49be-82a1-2eb1d1ae70cf"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "销售数量",
                        "columnId": "销售数量",
                        "columnName": "销售数量",
                        "dataType": "DECIMAL",
                        "defaultRecall": 0,
                        "fewShot": "11,1,2,3,14,4,5,6,7,8,9,10",
                        "modelCode": "sales_count",
                        "vectorUuid": "3164a12f-47fe-4fdd-9509-3507e8107087,e3d480ab-10d4-4227-a4f4-a9140d86b6a5,caa0230e-ae63-4731-aba4-3483b5549503,e84dfe99-a157-417a-ac28-79c4782e2979"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "区域",
                        "columnId": "区域",
                        "columnName": "区域",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "东北,中南,华北,华东,西南,西北",
                        "modelCode": "sales_count",
                        "vectorUuid": "be7a55f0-edb2-4975-a82c-d728d346212d,c35041ef-e1d6-4b3d-99fa-aae9b26273f4,d98a2713-e06a-4a90-8866-4415a29d4452,4fe30345-0980-42e7-955c-c26e200538e9"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "邮寄方式",
                        "columnId": "邮寄方式",
                        "columnName": "邮寄方式",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "二级,标准级,当日,一级",
                        "modelCode": "sales_count",
                        "vectorUuid": "13b211b4-4b71-4479-80a6-314f04ab8e02,afdf7364-d545-44ef-a7c3-4e04c744d595,09d66691-e620-4ef4-b2da-c831600fe344,36618abd-b7ed-44b6-89d9-2884b653f288"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "销售额",
                        "columnId": "销售额",
                        "columnName": "销售额",
                        "dataType": "DECIMAL",
                        "defaultRecall": 0,
                        "fewShot": "411.0120,4692.3800,235.4800,806.6800,496.1600,532.0000,502.4320,159.7680,3121.8600,426.7200,3277.2600,425.8800",
                        "modelCode": "sales_count",
                        "vectorUuid": "21988c6c-92c1-465e-b219-2665faaa195b,daa65a46-7d33-4ffe-be46-a3bfc019c7cc,577c2f6d-76a2-442c-ad15-f506e4310535,7e4586e2-604b-49f4-90be-8b5d0185a701"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "产品类型",
                        "columnId": "产品类型",
                        "columnName": "产品类型",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "技术,办公用品,家具",
                        "modelCode": "sales_count",
                        "vectorUuid": "0a70ecb6-4178-4bbb-af87-f0e684a524b6,a19ceb07-817a-4984-a4e4-a306fbe6221f,7d131006-12d7-4ba8-93fd-b9adcea903b4,81cce309-bd7e-443b-ae92-198538343abe"
                    },
                    {
                        "analyzeSuggest": 0,
                        "columnComment": "订单销售月份",
                        "columnId": "订单销售月份",
                        "columnName": "订单销售月份",
                        "dataType": "VARCHAR",
                        "defaultRecall": 0,
                        "fewShot": "2021-07,2021-06,2021-05,2021-04,2021-03,2021-02,2021-01,2021-12,2021-11,2021-10,2021-09,2021-08",
                        "modelCode": "sales_count",
                        "synonyms": "销售月份,下单月份",
                        "vectorUuid": "30484131-a118-430a-abaa-a408e34e526d,beeb5d26-2122-4d2c-8673-ee96da2eae03,ea22b600-5e69-493d-af38-c2cc1e2bc44a,23ec0275-f67d-43bc-9956-2e30a29869d1"
                    }
                ],
                "type": "sql",
                "usePrompt": "超市销售汇总数据"
            }
        ],
        "stream": True,
        "traceId": "b926ea9e-197d-402a-93e9-862b9a2c3725",
        "useElastic": True,
        "useVector": True,
        "userInfo": ""
    }
    
    rank_module = ColumnFilterModule(request_id=body["requestId"],
                                     query=body["query"],
                                     current_date_info=body["currentDateInfo"],
                                     table_id_list=body["modelCodeList"],
                                     column_info=body["schemaInfo"],)
    

        
    result = await rank_module.batch_get_result()
    
    print(result)
    
    
if __name__ == "__main__":
    asyncio.run(main())