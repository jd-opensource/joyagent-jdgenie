from .logger_utils import logger
from ..generation.vlm import VLLMClient


def generate_caption(image_path: str) -> str:
    try:
        client = VLLMClient()
        prompt = "描述图片的内容，不要超过100个字"
        messages = client.convert_messages_with_image_path(prompt, image_path)

        response = client.completions(messages, max_tokens=500, stream=False)

        return response
    except Exception as e:
        import traceback
        logger.error(traceback.format_exc())
        return ""