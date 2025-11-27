"""
文档离线处理模块

该模块负责对解析后的文档进行切分和预处理，然后存储到向量数据库：
- 文档切块（Chunking）
- 文本预处理和清洗
- 向量化处理
- 批量存储到向量数据库

主要功能：
1. 智能文档切分（基于语义、段落、句子等）
2. 图像内容提取和处理
3. 文档去重和去噪
4. 向量化并存储到Qdrant
5. 索引优化和管理
"""

import os
import time
import uuid

import requests
import tqdm
from PIL import Image
from loguru import logger

from .parser import get_document_parser
from .splitter import get_text_splitter
from ..embedding.bm25_embedding import get_bm25_embedding_model
from ..embedding.image_embedding import get_image_embedding_model
from ..embedding.text_embedding import get_text_embedding_model
from ..storage import VectorStore
from ..utils import image_utils, oss_utils
from ..utils.caption_utils import generate_caption
from ..utils.ocr_utils import get_ocr_model


def get_file_type(file_path: str):
    """获取文件的类型"""

    basename = os.path.basename(file_path)
    if "." in basename:
        return os.path.splitext(file_path)[1]
    else:
        raise ValueError(f"Unsupported file name: {file_path}")


class DocumentProcessor:
    """文档处理器类"""

    def __init__(self,
                 kb_id: str,
                 file_id: str,
                 work_dir: str,
                 file_path: str,
                 file_url: str
                 ):
        self._kb_id = kb_id
        self._work_dir = work_dir
        self._file_path = file_path
        self._file_type = get_file_type(file_path)
        self._filename = os.path.basename(file_path)
        self._parser = get_document_parser(self._file_type)(self._work_dir, self._file_path)
        self._file_url = file_url

        self._uid = file_id

        self._vector_store = VectorStore()

        self._text_embedding = get_text_embedding_model()

        self._bm25_embedding = get_bm25_embedding_model()

        self._image_embedding = get_image_embedding_model()

        self._ocr = get_ocr_model()
        self._image_urls = {}
        self.pre_process()

    def pre_process(self):
        """"""
        parser_start_time = time.time()
        self._parser.parse()
        for image_path in self._parser.parsed_images():
            image_url = oss_utils.upload_local_storage(image_path, file_id=self._uid)
            base_name = os.path.basename(image_path)
            self._image_urls[base_name] = image_url

        for path_path in self._parser.parsed_pages():
            image_url = oss_utils.upload_local_storage(path_path, file_id=self._uid)
            base_name = os.path.basename(path_path)
            self._image_urls[base_name] = image_url

        with open(self._parser.md_file_path, "r", encoding="utf-8") as f:
            text = f.read()

        for image_path in self._image_urls:
            # ![image_12.png](images/image_12.png)
            raw_md = f"![{os.path.basename(image_path)}](images/{image_path})"
            target_md = f"![{os.path.basename(image_path)}]({self._image_urls[image_path]})"
            logger.info(f"Processing text: {raw_md}\n ====> {target_md}")
            text = text.replace(raw_md, target_md)

        with open(self._parser.md_file_path, "w", encoding="utf-8") as f:
            f.write(text)

        parser_cost_time = time.time()

        logger.info(f"Parser cost time: {parser_cost_time - parser_start_time}s")

    def _process_text(self):
        text = self._parser.parsed_text()

        if not text:
            return

        chunk_texts = get_text_splitter().split(text=text)
        log_str = ""
        for i, chunk in enumerate(chunk_texts):
            log_str += f"=======================Chunk {i}: \n{chunk}\n"
        logger.debug(log_str)
        # 增加chunk的meta信息和
        batch_size = 10
        for i in tqdm.tqdm(range(0, len(chunk_texts), batch_size), desc="Processing text",
                           total=len(chunk_texts) // batch_size + 1):
            chunk_texts_batch = chunk_texts[i:i + batch_size]
            chunk_texts_embeddings = self._text_embedding.encode_text_batch(chunk_texts_batch)
            chunk_bm25_embeddings = self._bm25_embedding.encode_text_batch(chunk_texts_batch)
            chunk_data = [{
                "text": text,
                "vector": embedding,
                "sparse_vector": bm25_embedding,
                "kb_id": self._kb_id,
                "file_id": self._uid,
                "ref_id": self._uid,
                "doc_id": self._uid,
                "file_sorted": f"{self._uid}-{i + j}",
                "chunk_type": "text",
                "chunk_id": uuid.uuid4().hex,

                "file_path": self._file_path,
                "file_url": self._file_url,
                "filename": self._filename,
                "created": time.time(),
                "split_type": "default"

            }
                for j, (text, embedding, bm25_embedding) in
                enumerate(zip(chunk_texts_batch, chunk_texts_embeddings, chunk_bm25_embeddings))
            ]

            self._vector_store.add_text_chunks(chunk_data)
            logger.info(f"Processed {len(chunk_texts_batch)} text chunks")

        enable_sub_chunk = os.getenv("ENABLE_SUB_CHUNK_ENHANCE")

        sub_chunk_size = int(os.getenv("SUB_CHUNK_SIZE", 100))
        splitter = get_text_splitter(chunk_type="default", chunk_size=sub_chunk_size, chunk_overlap=0)
        sub_text_chunks = []
        sub_texts = []
        if enable_sub_chunk:
            for i, chunk_text in enumerate(chunk_texts):
                for sub_chunk_text in splitter.split(chunk_text):
                    sub_texts.append(sub_chunk_text)
                    sub_text_chunks.append({
                        "text": chunk_text,
                        "kb_id": self._kb_id,
                        "ref_id": self._uid,
                        "doc_id": self._uid,
                        "file_id": self._uid,
                        "file_sorted": f"{self._uid}-{i}",
                        "chunk_type": "text",
                        "chunk_id": uuid.uuid4().hex,

                        "file_path": self._file_path,
                        "file_url": self._file_url,
                        "filename": self._filename,
                        "created": time.time(),
                        "split_type": "default"
                    })
            for i in tqdm.tqdm(range(0, len(sub_texts), batch_size), desc="Processing sub text",
                               total=len(sub_texts) // batch_size + 1):
                sub_texts_batch = sub_texts[i:i + batch_size]
                sub_texts_embeddings = self._text_embedding.encode_text_batch(sub_texts_batch)
                sub_bm25_embeddings = self._bm25_embedding.encode_text_batch(sub_texts_batch)
                sub_chunk_data = sub_text_chunks[i:i + batch_size]
                for j, (chunk, embedding, bm25_embedding) in enumerate(
                        zip(sub_chunk_data, sub_texts_embeddings, sub_bm25_embeddings)):
                    chunk.update({
                        "vector": embedding,
                        "sparse_vector": bm25_embedding,
                    })
                self._vector_store.add_text_chunks(sub_chunk_data)

    def _process_image(self):
        image_paths = self._parser.parsed_images()

        batch_size = 5
        for i in tqdm.tqdm(range(0, len(image_paths), batch_size), desc="Process image",
                           total=len(image_paths) // batch_size + 1):
            image_paths_batch = image_paths[i:i + batch_size]
            images = [Image.open(image_path) for image_path in image_paths_batch]
            images = [image_utils.resize_image(image) for image in images]
            image_embeddings = self._image_embedding.encode_image_batch(images)

            # 添加到图片向量库
            chunk_data = []

            for j, (image_path, embedding) in enumerate(zip(image_paths_batch, image_embeddings)):
                base_name = os.path.basename(image_path)
                chunk_data.append({
                    "kb_id": self._kb_id,
                    "ref_id": self._uid,
                    "doc_id": self._uid,
                    "file_id": self._uid,
                    "image_id": f"{self._uid}-{i + j}",
                    "file_sorted": f"{self._uid}-{i + j}",
                    "chunk_id": uuid.uuid4().hex,

                    "chunk_type": "image",
                    "vector": embedding,
                    "file_path": self._file_path,
                    "image_path": image_path,
                    "file_url": self._file_url,
                    "filename": self._filename,
                    "created": time.time(),
                    "image_url": self._image_urls[base_name],
                })
            self._vector_store.add_image_chunks(chunk_data)

            # 生成ocr 和 caption
            text_chunk_data = []
            for j, image_path in enumerate(image_paths_batch):
                ocr_text = self._ocr.ocr(image_path)
                caption = generate_caption(image_path)
                base_name = os.path.basename(image_path)
                if ocr_text:
                    text_chunk_data.append({
                        "text": ocr_text,
                        "kb_id": self._kb_id,
                        "ref_id": self._uid,
                        "file_id": self._uid,
                        "doc_id": self._uid,
                        "chunk_id": uuid.uuid4().hex,
                        "image_id": f"{self._uid}-{i + j}",
                        "file_sorted": f"{self._uid}-{i + j}",
                        "chunk_type": "ocr_text",
                        "file_path": self._file_path,
                        "file_url": self._file_url,
                        "image_path": image_path,
                        "filename": self._filename,
                        "created": time.time(),
                        "image_url": self._image_urls[base_name],
                    })
                if caption:
                    text_chunk_data.append({
                        "text": caption,
                        "kb_id": self._kb_id,
                        "ref_id": self._uid,
                        "file_id": self._uid,
                        "doc_id": self._uid,
                        "chunk_id": uuid.uuid4().hex,

                        "image_id": f"{self._uid}-{i + j}",
                        "file_sorted": f"{self._uid}-{i + j}",
                        "chunk_type": "caption",
                        "file_path": self._file_path,
                        "file_url": self._file_url,
                        "image_path": image_path,
                        "filename": self._filename,
                        "created": time.time(),
                        "image_url": self._image_urls[base_name],
                    })
            text_batch = [chunk['text'] for chunk in text_chunk_data]
            text_embeddings = self._text_embedding.encode_text_batch(text_batch)
            bm25_embeddings = self._bm25_embedding.encode_text_batch(text_batch)
            for j, (chunk, embedding, bm25_embedding) in enumerate(
                    zip(text_chunk_data, text_embeddings, bm25_embeddings)):
                chunk.update({
                    "vector": embedding,
                    "sparse_vector": bm25_embedding,
                })
            self._vector_store.add_text_chunks(text_chunk_data)

    def _process_page(self):
        page_paths = self._parser.parsed_pages()

        batch_size = 5
        for i in tqdm.tqdm(range(0, len(page_paths), batch_size), desc="Process page",
                           total=len(page_paths) // batch_size + 1):
            page_paths_batch = page_paths[i:i + batch_size]
            pages = [Image.open(page_path) for page_path in page_paths_batch]
            pages = [image_utils.resize_image(page) for page in pages]
            image_embeddings = self._image_embedding.encode_image_batch(pages)

            # 添加到图片向量库
            chunk_data = []

            for j, (image_path, embedding) in enumerate(zip(page_paths_batch, image_embeddings)):
                base_name = os.path.basename(image_path)
                chunk_data.append({
                    "kb_id": self._kb_id,
                    "ref_id": self._uid,
                    "doc_id": self._uid,
                    "file_id": self._uid,
                    "chunk_id": uuid.uuid4().hex,

                    "page_id": f"{self._uid}-{i + j}",
                    "file_sorted": f"{self._uid}-{i + j}",
                    "chunk_type": "page",
                    "vector": embedding,
                    "file_path": self._file_path,
                    "file_url": self._file_url,
                    "page_path": image_path,
                    "filename": self._filename,
                    "created": time.time(),
                    "image_url": self._image_urls[base_name],
                })
            self._vector_store.add_page_chunks(chunk_data)

        text_chunk_data = []
        for j, image_path in enumerate(page_paths):
            ocr_text = self._ocr.ocr(image_path)
            caption = generate_caption(image_path)
            base_name = os.path.basename(image_path)
            if ocr_text:
                text_chunk_data.append({
                    "text": ocr_text,
                    "kb_id": self._kb_id,
                    "ref_id": self._uid,
                    "file_id": self._uid,
                    "doc_id": self._uid,
                    "chunk_id": uuid.uuid4().hex,

                    "page_id": f"{self._uid}-{j}",
                    "file_sorted": f"{self._uid}-{j}",
                    "chunk_type": "ocr_text",
                    "file_path": self._file_path,
                    "file_url": self._file_url,
                    "page_path": image_path,
                    "filename": self._filename,
                    "created": time.time(),
                    "image_url": self._image_urls[base_name],
                })
            if caption:
                text_chunk_data.append({
                    "text": caption,
                    "kb_id": self._kb_id,
                    "ref_id": self._uid,
                    "file_id": self._uid,
                    "doc_id": self._uid,
                    "chunk_id": uuid.uuid4().hex,

                    "page_id": f"{self._uid}-{j}",
                    "file_sorted": f"{self._uid}-{j}",
                    "chunk_type": "caption",
                    "file_path": self._file_path,
                    "file_url": self._file_url,
                    "page_path": image_path,
                    "filename": self._filename,
                    "created": time.time(),
                    "image_url": self._image_urls[base_name],
                })
        text_batch = [chunk['text'] for chunk in text_chunk_data]
        text_embeddings = self._text_embedding.encode_text_batch(text_batch)
        bm25_embeddings = self._bm25_embedding.encode_text_batch(text_batch)
        for j, (chunk, embedding, bm25_embedding) in enumerate(
                zip(text_chunk_data, text_embeddings, bm25_embeddings)):
            chunk.update({
                "vector": embedding,
                "sparse_vector": bm25_embedding,
            })
        self._vector_store.add_text_chunks(text_chunk_data)

    def _mrag_process(self):
        self._process_text()

        self._process_image()

        self._process_page()

    def _lightrag_process(self):
        lightrag_base_url = os.getenv('LIGHTRAG_SERVER_BASE_URL')
        if not lightrag_base_url:
            logger.warning("LIGHTRAG_SERVER_BASE_URL environment variable not set, skip lightrag process")
            return
        text = self._parser.parsed_text()
        url = f"{os.getenv('LIGHTRAG_SERVER_BASE_URL')}/documents/text"

        data = {
            "text": text
        }
        try:
            response = requests.post(url, json=data, timeout=300)
            if response.status_code != 200:
                raise Exception(f"LightRAG 请求失败: {response.text}")
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
            logger.error(f"LightRAG 请求失败: {e}")
            return

    def process(self):
        mrag_start_time = time.time()
        self._mrag_process()
        mrag_cost_time = time.time()
        logger.info(f"MRAG cost time: {mrag_cost_time - mrag_start_time}")
        light_rag_start_time = time.time()
        self._lightrag_process()
        light_rag_cost_time = time.time()
        logger.info(f"LightRAG cost time: {light_rag_cost_time - light_rag_start_time}")
