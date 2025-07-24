# -*- coding: utf-8 -*-
# =====================
#
#
# Author: liumin.423
# Date:   2025/7/7
# =====================
import asyncio
import importlib
import os
import shutil
import tempfile
from typing import List, Optional

import pandas as pd
import yaml
from jinja2 import Template
from smolagents import LiteLLMModel, FinalAnswerStep, PythonInterpreterTool, ChatMessageStreamDelta

from genie_tool.tool.ci_agent import CIAgent
from genie_tool.util.file_util import download_all_files_in_path, upload_file, upload_file_by_path
from genie_tool.util.log_util import timer
from genie_tool.util.prompt_util import get_prompt
import requests
from genie_tool.model.code import ActionOutput, CodeOuput

@timer()
async def code_interpreter_agent(
    task: str,
    file_names: Optional[List[str]] = None,
    max_file_abstract_size: int = 2000,
    max_tokens: int = 32000,
    request_id: str = "",
    stream: bool = True,
):
    work_dir = ""
    try:
        work_dir = tempfile.mkdtemp()
        output_dir = os.path.join(work_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        import_files = await download_all_files_in_path(file_names=file_names, work_dir=work_dir)

        # 1. 文件处理
        files = []
        if import_files:
            for import_file in import_files:

                file_name = import_file["file_name"]

                file_path = import_file["file_path"]
                if not file_name or not file_path:
                    continue

                # 表格文件
                if file_name.split(".")[-1] in ["xlsx", "xls", "csv"]:
                    pd.set_option("display.max_columns", None)
                    df = (
                        pd.read_csv(file_path)
                        if file_name.endswith(".csv")
                        else pd.read_excel(file_path)
                    )
                    files.append({"path": file_path, "abstract": f"{df.head(10)}"})
                # 文本文件
                elif file_name.split(".")[-1] in ["txt", "md", "html"]:
                    with open(file_path, "r") as rf:
                        files.append(
                            {
                                "path": file_path,
                                "abstract": "".join(rf.readlines())[
                                    :max_file_abstract_size
                                ],
                            }
                        )

        # 2. 构建 Prompt
        ci_prompt_template = get_prompt("code_interpreter")

        # 3. CodeAgent
        agent = create_ci_agent(
            prompt_templates=ci_prompt_template,
            max_tokens=max_tokens,
            return_full_result=True,
            output_dir=output_dir,
        )

        template_task = Template(ci_prompt_template["task_template"]).render(
            files=files, task=task, output_dir=output_dir
        )

        if stream:
            for step in agent.run(task=str(template_task), stream=True, max_steps=10):
                if isinstance(step, CodeOuput):
                    file_info = await upload_file(
                        content=step.code,
                        file_name=step.file_name,
                        file_type="py",
                        request_id=request_id,
                    )
                    step.file_list = [file_info]
                    yield step
                
                elif isinstance(step, FinalAnswerStep):
                    file_list = []
                    file_path = get_new_file_by_path(output_dir=output_dir)
                    if file_path:
                        file_info = await upload_file_by_path(
                            file_path=file_path, request_id=request_id
                        )
                        if file_info:
                            file_list.append(file_info)
                    code_name = f"{task[:20]}_代码输出.md"
                    file_list.append(
                        await upload_file(
                            content=step.output,
                            file_name=code_name,
                            file_type="md",
                            request_id=request_id,
                        )
                    )

                    output = ActionOutput(content=step.output, file_list=file_list)
                    yield output
                elif isinstance(step, ChatMessageStreamDelta):
                    #yield step.content
                    pass
                await asyncio.sleep(0)
                
        else:
            output = agent.run(task=task)
            yield output
    except Exception as e:
        raise e

    finally:
        if work_dir:
            shutil.rmtree(work_dir, ignore_errors=True)


def get_new_file_by_path(output_dir):
    temp_file = ""
    latest_time = 0
    for item in os.listdir(output_dir):
        if item.endswith(".xlsx") or item.endswith(".csv") or item.endswith(".xls"):
            item_path = os.path.join(output_dir, item)
            if os.path.isfile(item_path):
                # 获取文件的最后修改时间
                mod_time = os.path.getmtime(item_path)
                # 如果当前文件比之前记录的更新，则更新最新文件和时间为当前文件
                if mod_time > latest_time:
                    latest_time = mod_time
                    temp_file = item_path
    return temp_file


def create_ci_agent(
    prompt_templates=None,
    max_tokens: int = 16000,
    return_full_result: bool = True,
    output_dir: str = "",
) -> CIAgent:
    model = LiteLLMModel(
        max_tokens=max_tokens,
        model_id=os.getenv("CODE_INTEPRETER_MODEL","gpt-4.1")
    )

    return CIAgent(
        model=model,
        prompt_templates=prompt_templates,
        tools=[PythonInterpreterTool()],
        return_full_result=return_full_result,
        additional_authorized_imports=[
            "pandas",
            "openpyxl",
            "numpy",
            "matplotlib",
            "seaborn",
        ],
        output_dir=output_dir,
    )


if __name__ == "__main__":
    pass
