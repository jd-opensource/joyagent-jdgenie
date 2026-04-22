# coding=utf-8
import json
import os
import time
from typing import Optional

from dotenv import load_dotenv

import requests
from genie_tool.util.log_util import logger
from genie_tool.tool.table_rag.es_client import ElasticsearchClient
from genie_tool.tool.table_rag.qdrant_recall import get_qd_recall, get_qd_server_recall

# 加载 .env 文件
load_dotenv()


def retrieved_cells_dict2map_key_val(retrieved_cells_dict, _few_shot_seprator):
    # 按 modelCode-columnId 聚合ES召回的多条文档，将value拼接
    _map = {}
    for key, item in retrieved_cells_dict.items():
        assert "columnId" in item and "modelCode" in item, item
        column_id = item["columnId"]
        table_id = item["modelCode"]
        key = f"{table_id}-{column_id}"
        
        if key not in _map:
            few_shot_value = item["value"] if item["value"] else ""
            del item["value"]
            _map[key] = {
                "value": few_shot_value,
                "schema": item,
            }
        
        else:
            # 更新value
            few_shot_value = _map[key]["value"]
            few_shot_value += _few_shot_seprator + item["value"] if item["value"] else ""
            _map[key]["value"] = few_shot_value
    return _map


def retrieved_list2map_schema(retrieved_list):
    _map = {}
    for item in retrieved_list:
        assert "columnId" in item and "modelCode" in item, item
        column_id = item["columnId"]
        table_id = item["modelCode"]
        key = f"{table_id}-{column_id}"
        
        if key not in _map:
            _map[key] = item
        
    return _map


class Retriever:
    def __init__(self, request_id):
        self.es_recall_top_k = os.getenv("TR_ES_RECALL_TOP_K")

        self.request_id = request_id

        self.es_client = self.get_es_client()
        
    def get_es_client(self):
        # 读取环境变量
        config = {}
        config["host"] = os.getenv("TR_ES_CONFIGS_HOST")
        config["port"] = os.getenv("port")
        config["scheme"] = "http"
        config["user"] = os.getenv("TR_ES_CONFIGS_USER")
        config["password"] = os.getenv("TR_ES_CONFIGS_PASSWORD")
        self.es_index = os.getenv("TR_ES_CONFIGS_INDEX", None)

        es_client = ElasticsearchClient(config)
        return es_client

    def es_recall(self, query : str ="cho人数",
                  model_code_list: Optional[str] = []):
        search_body = {"query": query,
                       "model_code_list": model_code_list,
                       "size": self.es_recall_top_k}
        res = self.es_client.search_body(self.es_index, search_body=search_body)
        return res

    async def qdrant_recall(self, query, model_code_list):
        QDRANT_ENABLE = os.getenv("TR_QDRANT_ENABLE", "false").lower() == "true"
        TR_QDRANT_HOST = os.getenv("TR_QDRANT_HOST", None)
        TR_QDRANT_URL = os.getenv("TR_QDRANT_URL", None)
        if not QDRANT_ENABLE:
            return []
        if TR_QDRANT_URL:
            data = get_qd_server_recall(query, model_code_list)
        elif TR_QDRANT_HOST:
            data = get_qd_recall(query, model_code_list)
        else:
            data = []
        
        if data is None:
            data = []
        if not data:
            logger.error(f"No data found for {query}")
        return {"data": data}

    async def retrieve_schema(self, query, model_code_list):
        # 召回列名
        data = await self.qdrant_recall(query, model_code_list)
        
        return data

    async def retrieve_cell(self, query, model_code_list):
        # 召回值
        data = self.es_recall(query, model_code_list)
        return {"data": data}
    
    def qd_merge_rerank(self, qdrant_results):
        merge_map = {}
        for result in qdrant_results:
            key = result["modelCode"] + "-" + result["columnId"]
            if key not in merge_map:
                merge_map[key] = {
                    "schema": result,
                    "score": result["score"],
                }
            
            else:
                merge_map[key]["score"] += result["score"]
        
        # to list
        schema_list = []
        for key, result in merge_map.items():
            result["schema"]["score"] = result["score"]
            schema_list.append(result["schema"])
        
        # column score
        schema_list = sorted(schema_list, key=lambda k: k["score"], reverse=True)
        
        return schema_list
    
    @staticmethod
    def _dedup_fewshot(fewshot_str):
        """对合并后的fewShot字符串进行去重
        
        fewShot可能包含 ',' 和 ';' 两种分隔符（Qdrant用逗号，ES用分号），
        统一拆分后去重，再用逗号拼回。
        """
        if not fewshot_str:
            return ""
        import re
        values = re.split(r'[;,]', fewshot_str)
        seen = set()
        unique_values = []
        for v in values:
            v_stripped = v.strip()
            if v_stripped and v_stripped not in seen:
                seen.add(v_stripped)
                unique_values.append(v_stripped)
        return ",".join(unique_values)

    def qd_es_merge(self, retrieved_cells, retrieved_columns):
        # retrieved_cells
        _few_shot_seprator = ";"
        retrieved_cells_key_val_map = retrieved_cells_dict2map_key_val(retrieved_cells, _few_shot_seprator)
        retrieved_columns_schema_map = retrieved_list2map_schema(retrieved_columns)
        # 需要把retrieveled few shots 放到columns里面去
        for key, schema_val in retrieved_cells_key_val_map.items():
            
            if key in retrieved_columns_schema_map:
                _few_shot = retrieved_columns_schema_map[key]["fewShot"]
                if _few_shot:
                    _few_shot = schema_val["value"] + _few_shot_seprator + _few_shot
                else:
                    _few_shot = schema_val["value"]
            else:
                retrieved_columns_schema_map[key] = schema_val["schema"]
                _few_shot = schema_val["value"]
            
            # 去重（ES召回value可能与Qdrant fewShot存在重叠）
            _few_shot = self._dedup_fewshot(_few_shot)
            retrieved_columns_schema_map[key]["fewShot"] = _few_shot
            
        retrieved_columns_schema_list = [val for key, val in retrieved_columns_schema_map.items()]
        return retrieved_columns_schema_list
