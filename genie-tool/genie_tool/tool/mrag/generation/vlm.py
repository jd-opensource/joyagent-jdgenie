import base64
import os
import tempfile
import uuid
from pathlib import Path

from openai import OpenAI

from genie_tool.tool.mrag.utils import download_utils
from genie_tool.tool.mrag.utils.logger_utils import logger

class VLLMClient:
    """大模型客户端类"""

    # 配置环境变量
    # API_KEY llm 大模型apikey
    # LLM_MODEL_NAME 大模型名称
    # LLM_MODEL_BASE_URL 大模型地址
    def __init__(self, base_url=None, model_name=None, api_key=None):
        self.api_key = api_key or os.getenv("VLM_API_KEY")
        self.model_name = model_name or os.getenv("VLM_MODEL_NAME")
        self.model_base_url = base_url or os.getenv("VLM_MODEL_BASE_URL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.model_base_url
        )
        logger.info(f"VLM Client {self.model_base_url}")

    @staticmethod
    def convert_messages(prompt, image_url):
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]

    @staticmethod
    def convert_messages_with_image_path(prompt, image_path: str):
        image_url = image_path
        if image_path.startswith("http"):
            image_path = image_path.split("/")[-1]
            temp_dir = tempfile.gettempdir()
            uid = uuid.uuid4().hex
            _dir = os.path.join(temp_dir, uid)
            os.makedirs(_dir, exist_ok=True)
            image_path = os.path.join(_dir, image_path)
            download_utils.download_file(image_url, image_path)

        def _encode_image() -> str:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        def _get_image_mime_type() -> str:
            suffix = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            return mime_types.get(suffix, 'image/jpeg')

        base64_image = "data:" + _get_image_mime_type() + ";base64," + _encode_image()

        if image_path.startswith("http"):
            os.remove(image_path)

        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image
                        }
                    }
                ]
            }
        ]

    def completions(self, messages, temperature=0, stream=False, max_tokens: int = None):
        # logger.info(f"VLM completions {messages[:1]}")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            stream=stream,
            max_tokens=max_tokens,
            extra_body={"enable_thinking": False}
        )
        if stream:
            return completion
        return completion.choices[0].message.content

    def chat(self, prompt, image_url):
        messages = self.convert_messages(prompt, image_url)
        return self.completions(messages)


if __name__ == '__main__':
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "提取图片中所有内容。\n    输出:\n "
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://autobots.jd.com/autobots/interface/oss/downloadFile?ossName=joyspace-img/fd93bdf1aaf7ac2abea6315950176f2b.png"
                    }
                }
            ]
        }
    ]
    os.environ.setdefault("VLM_API_KEY", "")
    os.environ.setdefault("VLM_MODEL_NAME", "OpenGVLab/InternVL3_5-8B-MPO")
    os.environ.setdefault("VLM_MODEL_BASE_URL", "http://internvl3d5-8b-mpo-4090d-svc.jd.local/v1")
    llm = VLLMClient()
    print(llm.completions(messages))
