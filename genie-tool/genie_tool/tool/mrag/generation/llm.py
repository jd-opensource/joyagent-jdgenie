import os

import dotenv
from openai import OpenAI
from genie_tool.util.log_util import logger
dotenv.load_dotenv()


class LLMClient:
    """大模型客户端类"""

    # 配置环境变量
    # API_KEY llm 大模型apikey
    # LLM_MODEL_NAME 大模型名称
    # LLM_MODEL_BASE_URL 大模型地址
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.model_name = os.getenv("LLM_MODEL_NAME")
        self.model_base_url = os.getenv("LLM_MODEL_BASE_URL")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.model_base_url
        )
        logger.info("init LLM client, {base_url}".format(base_url=self.model_base_url))

    @staticmethod
    def convert_messages(prompt):
        return [{"role": "user", "content": prompt}]

    def completions(self, messages, max_tokens=8192, temperature=0, stream=False):
        logger.info(f"chat completion\n{self.model_name}, {messages}")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            stream=stream,
            max_tokens=max_tokens,
            extra_body={"enable_thinking": False,
                        "chat_template_kwargs": {
                            "enable_thinking": False
                        }}
        )
        if stream:
            return completion
        return completion.choices[0].message.content

    def chat(self, prompt, image_url):
        messages = self.convert_messages(prompt)
        return self.completions(messages)


if __name__ == '__main__':
    os.environ.setdefault("API_KEY", "Bearer sk-8a885913ec6044d38e6f167e4b1f6380")
    os.environ.setdefault("LLM_MODEL_NAME", "qwen-plus")
    os.environ.setdefault("LLM_MODEL_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    llm = LLMClient()
    print(llm.completions([{"role": "user", "content": "你好"}]))
