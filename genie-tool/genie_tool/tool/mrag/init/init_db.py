import os

import dotenv
import requests

from genie_tool.tool.mrag.storage import VectorStore
from genie_tool.tool.mrag.utils.oss_utils import upload_local_storage

dotenv.load_dotenv()

base_url = "http://127.0.0.1:1601"


def create_knowledge_base(kb_id: str):
    """
    创建知识库
    """
    if not kb_id:
        raise ValueError("kb_id is required")

    body = {
        "kb_id": kb_id,
        "kb_name": "local_mrag",
        "kb_desc": "本地多模态知识库"
    }

    response = requests.post(f"{base_url}/v1/documents/create_knowledge_base", json=body, timeout=300)
    if response.status_code == 200:
        print("创建知识库成功")
    else:
        print("创建知识库失败")


def delete_knowledge_base(kb_id: str):
    """
    删除知识库
    """
    body = {
        "kb_id": kb_id
    }

    response = requests.post(f"{base_url}/v1/documents/delete_knowledge_base", json=body, timeout=300)
    if response.status_code == 200:
        print("删除知识库成功")
    else:
        print("删除知识库失败")


def submit_add_file_task(file_url: str, file_name: str, kb_id: str = None):
    body = {
        "kb_id": kb_id,
        "files": [{
            "file_url": file_url,
            "filename": file_name,
        }]
    }

    response = requests.post(f"{base_url}/v1/documents/add_files", json=body, timeout=300)
    if response.status_code == 200:
        print("提交文件成功")
    else:
        print("提交文件失败")


def init_local_kb():
    """
    初始化本地知识库

    """
    kb_id = os.getenv("DEFAULT_KB_ID")
    delete_knowledge_base(kb_id)

    create_knowledge_base(kb_id)

    data_dir = os.path.join(os.path.dirname(__file__), "mrag_data")

    for _dir, _, files in os.walk(data_dir):
        for file in files:
            local_path = os.path.join(_dir, file)
            file_url = upload_local_storage(local_path)
            print(f"上传文件: {file} -> {file_url}")
            submit_add_file_task(file_url, file, kb_id)


if __name__ == "__main__":
    vs = VectorStore()
    vs.create_all_collections()
    init_local_kb()