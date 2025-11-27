"""
Agentic RAG模块

该模块实现智能化的RAG系统，具备推理和决策能力：
- 智能查询规划
- 多步推理
- 工具调用
- 自我反思和优化

主要功能：
1. 查询分解和规划
2. 多步推理和验证
3. 外部工具调用集成
4. 结果评估和自我修正
5. 对话记忆管理
6. 个性化推荐策略
"""
import concurrent.futures
import uuid
from typing import List, Dict, Tuple

from .query_processor import QueryProcessor
from ..generation import PromptManager
from ..generation.llm import LLMClient
from ..generation.vlm import VLLMClient
from ..rerank.text_reranker import get_text_reranker
from ..retrieval import BaseRetriever
from ..utils.logger_utils import logger
from ..utils.time_utils import time_it


def beautify_messages(messages: List):
    output_content = ""
    for message in messages:
        content = message["content"]
        if isinstance(content, list):
            content = "\n".join([c["text"][:100] if c["type"] == "text" else "[图片]" for c in content])
        else:
            content = message["content"]
            if len(content) > 100:
                content = content[:100] + "..."
        output_content += f"[{message['role']}]: {content}\n"
    return output_content


def display_chunks(chunks: List[Dict]):
    for i, chunk in enumerate(chunks):
        print(f"=======================Chunk {i}: ")
        print(f"score: {chunk['score']}")
        print(f"chunk: {chunk['payload']['text'][:100]}")


class AgenticRAG:
    """智能RAG系统类"""

    def __init__(self, kb_id: str, n_round: int = 5):
        self._n_round = n_round
        self._retriever = BaseRetriever()
        self._kb_id = kb_id

    def retrieval(self, questions: list[str]) -> List[List[Dict]]:
        text_resp = self._retriever.retrieval_by_texts(self._kb_id, questions)
        return text_resp

    @staticmethod
    def merge_retrieval_results(resp: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        # 根据类型， 去重
        text_chunk_map = {}
        image_chunk_map = {}
        page_chunk_map = {}
        for ret in resp:
            chunk_type = ret['payload']['chunk_type']
            if chunk_type == "text":
                # print(ret)
                key = ret['payload']['file_sorted']
                text_chunk_map[key] = ret
            elif chunk_type == "image" or chunk_type == "ocr_text" or chunk_type == "caption":
                # print("image: ", ret)
                if "image_id" in ret['payload']:
                    key = ret['payload']['image_id']
                    image_chunk_map[key] = ret
                elif "page_id" in ret['payload']:
                    key = ret['payload']['page_id']
                    page_chunk_map[key] = ret
            elif chunk_type == "page":
                key = ret['payload']['page_path']
                page_chunk_map[key] = ret

        text_chunks = list(sorted(text_chunk_map.values(), key=lambda k: k['score'], reverse=True))
        image_chunks = list(sorted(image_chunk_map.values(), key=lambda k: k['score'], reverse=True))
        page_chunks = list(sorted(page_chunk_map.values(), key=lambda k: k['score'], reverse=True))

        def build_text_context():
            context = "文本检索内容：\n"
            for doc in text_chunks:
                context += doc["payload"]['text'][:100] + "\n"

            print(context)

        def build_image_context():
            context = ""
            for doc in image_chunks:
                context += f'{doc["payload"]["image_path"]} {doc["score"]}' + "\n"
            print(context)

        def build_page_context():
            context = ""
            for doc in page_chunks:
                context += f'{doc["payload"]["page_path"]} {doc["score"]}' + "\n"
            print(context)

        # build_text_context()
        build_image_context()
        build_page_context()

        return text_chunks, image_chunks, page_chunks

    @staticmethod
    def build_ref_context(docs: List[Dict]):
        context = ""
        for i, doc in enumerate(docs):
            if doc['payload'].get("text"):
                context += f"\n[ref {i + 1} start]\n{doc['payload']['text']}\n[ref {i + 1} end]\n"
        return context

    @time_it
    def multi_retrieval(self, questions: List[str]):
        # 多路检索查询
        results = self.retrieval(questions)
        return results

    @staticmethod
    def llm_answer(question: str):
        prompt = PromptManager.DEFAULT_PROMPT.format(question=question)
        messages = LLMClient.convert_messages(prompt)
        response = LLMClient().completions(messages, stream=True, )
        return response

    @staticmethod
    def vlm_answer(question: str, image_urls: List[str]):
        prompt = f"根据图片回答问题：{question}"
        client = VLLMClient()
        messages = client.convert_messages_with_image_path(prompt, image_urls[0])
        response = client.completions(messages, stream=True)
        return response

    def fast_answer(self, question: str, image_urls: List[str] = None):
        if not image_urls:
            return self.llm_answer(question)
        else:
            return self.vlm_answer(question, image_urls)

    @time_it
    def run(self, question: str, image_urls: List[str] = None):
        logger.info(f"AIAgent: {question}, {image_urls}")
        if image_urls:
            image_descs = [QueryProcessor.extract_image_content(uuid.uuid4().hex, image_url) for image_url in
                           image_urls]
        else:
            image_descs = []

        # 0.判断用户的问题是否需要检索
        simple_check_flag = QueryProcessor.simple_query_check(question)
        if simple_check_flag:
            yield from self.llm_answer(question)
            return

        simple_image_query = QueryProcessor.simple_image_query_check(question, image_descs)
        if simple_image_query:
            yield from self.vlm_answer(question, image_urls)
            return

        loop = 1
        # Agentic RAG
        answer_question = question

        total_sub_questions = []
        total_sub_summaries = []

        total_chunks = []

        while True:
            logger.info(f"第{loop}轮查询")
            # 1. 生成子查询
            if loop == 1 and image_urls:
                sub_questions = QueryProcessor.expand_question_with_images(answer_question, image_descs)
            else:
                sub_questions = QueryProcessor.extend_questions(answer_question)

            if loop == 1:
                sub_questions.insert(0, question)

            total_sub_questions.extend(sub_questions)

            # 2. 执行检索阶段
            logger.info("开始多路检索阶段")
            current_chunks = self.multi_retrieval(sub_questions)

            for query_chunks in current_chunks:
                for chunk in query_chunks:
                    # logger.info(f"检索结果: {chunk['payload']}")
                    total_chunks.append(chunk)

            loop += 1
            if loop > 3:
                break

            # 总结多路召回的结果
            tasks = {}
            summarized_infos = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                for sub_question, query_chunks in zip(sub_questions, current_chunks):
                    task = executor.submit(QueryProcessor.summarize_subquery, sub_question, query_chunks)
                    tasks[task] = sub_question

                for future in concurrent.futures.as_completed(tasks):
                    sub_question = tasks[future]
                    try:
                        result = future.result()
                        logger.info(f"总结结果: {result}")
                        summarized_infos[sub_question] = result
                    except Exception as e:
                        logger.error(f"Error occurred while summarizing {sub_question}: {e}")

            # 记录每个子查询的结果
            for sub_question in sub_questions:
                total_sub_summaries.append(summarized_infos[sub_question])

            # 检查已经的检索信息是否充分
            next_instruction = QueryProcessor.generate_next_instruction(question, total_sub_questions,
                                                                        total_sub_summaries)

            # 信息已经充分开始回答
            if next_instruction['is_answer']:
                break
            else:
                answer_question = next_instruction['rewrite_query']
        # Ans
        text_chunks, image_chunks, page_chunks = self.merge_retrieval_results(total_chunks)

        logger.info(
            f"Agentic search results: 文本: {len(text_chunks)}, 图片: {len(image_chunks)}, 页面: {len(page_chunks)}")

        # page_chunks 过滤
        page_chunks = page_chunks[:1]

        # 3. 文本重排
        logger.info("开始重排阶段")
        texts = [text_chunk['payload']['text'] for text_chunk in text_chunks]
        scores = get_text_reranker().rerank(question, texts)

        for text_chunk, score in zip(text_chunks, scores):
            text_chunk['score'] = score

        text_chunks = sorted(text_chunks, key=lambda k: k['score'], reverse=True)
        # 重排结果
        display_chunks(text_chunks)

        text_chunks = [text_chunk for text_chunk in text_chunks if text_chunk['score'] > 0.3]

        if not text_chunks:
            logger.info("没有找到文本检索结果")

            if page_chunks:
                logger.info("使用图片问答")
                image_urls = [page_chunk['payload']['image_url'] for page_chunk in page_chunks]
                chunk = None
                for chunk in self.vlm_answer(question, image_urls):
                    yield chunk
                # 返回图片链接
                if chunk:
                    chunk.choices[0].delta.content = f"\n\n![图片]({image_urls[0]})"
                    yield chunk
                return

            logger.info("使用LLM回答")
            yield from self.fast_answer(question, image_urls)
            return

        context = self.build_ref_context(text_chunks)

        if not page_chunks:
            logger.info("没有找到图片, 使用LLM回答")
            prompt = PromptManager.TEXT_PROMPT.format(context=context, question=question)
            messages = LLMClient().convert_messages(prompt)

            response = LLMClient().completions(messages, stream=True)
            yield from response
            return

        logger.info("使用多模态模型回答")
        prompt = PromptManager.IMAGE_PROMPT.format(context=context, question=question)
        image_paths = [page_chunk['payload']['image_url'] for page_chunk in page_chunks]

        image_path = image_paths[0]

        client = VLLMClient()
        messages = client.convert_messages_with_image_path(prompt, image_path)

        response = client.completions(messages, stream=True)
        chunk  = None
        for chunk in response:
            yield chunk
        if chunk:
            chunk.choices[0].delta.content = f"\n\n![图片]({image_path})"
            yield chunk

