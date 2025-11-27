import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...document import DocumentProcessor
from ...enums.source_type_enums import SourceTypeEnum
from ...enums.task_status_enums import TaskStatusEnum
from ...storage import VectorStore
from ...storage.models.kb_file_model import KBFileModel
from ...storage.models.kb_model import KBModel
from ...storage.store_factory import get_kb_store, get_kb_file_store
from ...utils import download_utils, crawl_utils
from ...utils.logger_utils import logger
from ...utils.oss_utils import upload_oss

router = APIRouter(prefix="/documents", tags=["文档处理"])

# 支持的文件类型
SUPPORTED_FILE_TYPES = {
    # 文档类型
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    # 图片类型
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
    'image/png': '.png',
    'image/gif': '.gif',
    'image/bmp': '.bmp',
    'image/webp': '.webp',
    'image/tiff': '.tiff',
    'image/tif': '.tif',
    'image/svg+xml': '.svg'
}

# 最大文件大小 (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档和图片到OSS并返回访问链接
    
    支持的文件类型: 
    - 文档: PDF, DOC, DOCX, TXT, XLS, XLSX, PPT, PPTX
    - 图片: JPG, JPEG, PNG, GIF, BMP, WEBP, TIFF, TIF, SVG
    最大文件大小: 50MB
    
    返回:
        - document_id: 文档唯一标识
        - filename: 原始文件名
        - file_size: 文件大小(字节)
        - content_type: 文件类型
        - upload_time: 上传时间
        - permanent_url: 永久访问链接
        - presigned_url: 临时访问链接(30天有效)
    """
    print(file)
    try:
        # 验证文件类型
        if file.content_type:
            if file.content_type not in SUPPORTED_FILE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {file.content_type}。支持的类型: {', '.join(SUPPORTED_FILE_TYPES.values())}"
                )
        else:
            file_extension = os.path.splitext(file.filename)[1]
            if file_extension not in SUPPORTED_FILE_TYPES.values():
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的文件类型: {file_extension}。支持的类型: {', '.join(SUPPORTED_FILE_TYPES.values())}"
                )

        # 读取文件内容并验证大小
        file_content = await file.read()
        file_size = len(file_content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制。最大允许: {MAX_FILE_SIZE // (1024 * 1024)}MB，当前文件: {file_size // (1024 * 1024)}MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="文件为空")

        # 生成文档ID和文件名
        document_id = str(uuid.uuid4())
        file_extension = SUPPORTED_FILE_TYPES.get(file.content_type, '')

        # 确保文件名有正确的扩展名
        original_filename = file.filename
        if not original_filename.lower().endswith(file_extension.lower()):
            safe_filename = f"{Path(original_filename).stem}{file_extension}"
        else:
            safe_filename = original_filename

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        logger.info(f"文件暂存到: {temp_file_path}")
        try:
            # 上传到OSS
            # 使用日期作为目录结构: documents/YYYY/MM/DD/
            upload_date = datetime.now()
            oss_dir = f"documents/{upload_date.year:04d}/{upload_date.month:02d}/{upload_date.day:02d}"

            logger.info(f"开始上传文档到OSS: {safe_filename}, 大小: {file_size} bytes")

            success, permanent_url, presigned_url = upload_oss(
                file_path=temp_file_path,
                dir_=oss_dir,
                is_delete=False
            )

            if not success:
                raise HTTPException(status_code=500, detail="文件上传到OSS失败")

            logger.info(f"文档上传成功: {document_id}, 永久链接: {permanent_url}")

            # 返回上传结果
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "文档上传成功",
                    "data": {
                        "document_id": document_id,
                        "filename": safe_filename,
                        "original_filename": original_filename,
                        "file_size": file_size,
                        "content_type": file.content_type,
                        "upload_time": upload_date.isoformat(),
                        "permanent_url": permanent_url,
                        "presigned_url": presigned_url,
                        "oss_path": f"{oss_dir}/{safe_filename}"
                    }
                }
            )

        except Exception as e:
            # 确保清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文档上传过程中发生错误: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


class CreateKnowledgeBaseRequest(BaseModel):
    kb_id: Optional[str]
    kb_name: Optional[str]
    kb_desc: Optional[str]
    chunk_type: Optional[str] = Field("fixed_size", description="chunk_type")
    chunk_size: Optional[int] = Field(None, description="chunk_size")
    chunk_overlap_size: Optional[int] = Field(None, description="chunk_overlap_size")


@router.post("/create_knowledge_base")
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    kb_store = get_kb_store()
    if not request.kb_id:
        request.kb_id = uuid.uuid4().hex
    kb_id = request.kb_id
    kb_model = KBModel(
        kb_id=kb_id,
        kb_name=request.kb_name,
        kb_desc=request.kb_desc,
        chunk_type=request.chunk_type,
        chunk_size=request.chunk_size,
        chunk_overlap_size=request.chunk_overlap_size,
        create_time=datetime.now(),
        modify_time=datetime.now(),
    )
    kb_store.create_kb(kb_model)

    res = {
        "code": 200,
        "msg": "success",
        "data": kb_model.model_dump()
    }
    logger.info(f"create knowledge base, {res}")
    return res


class DeleteKnowledgeBaseRequest(BaseModel):
    kb_id: Optional[str]


@router.post("/delete_knowledge_base")
async def delete_knowledge_base(request: DeleteKnowledgeBaseRequest):
    kb_store = get_kb_store()
    kb_model = KBModel(kb_id=request.kb_id)
    kb_store.delete_kb(kb_model)

    VectorStore().delete_text_by_kb_id(request.kb_id)
    VectorStore().delete_image_by_kb_id(request.kb_id)
    VectorStore().delete_page_by_kb_id(request.kb_id)

    return {
        "code": 200,
        "msg": "success",
        "data": {}
    }


class ListKnowledgeBaseRequest(BaseModel):
    page_no: Optional[int] = Field(1, description="page_no")
    page_size: Optional[int] = Field(10, description="page_size")


@router.post("/list_knowledge_base")
async def list_knowledge_base(request: ListKnowledgeBaseRequest):
    kb_store = get_kb_store()
    kb_models = kb_store.get_kbs(request.page_no, request.page_size)
    res = {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [kb_model.model_dump() for kb_model in kb_models],
            "page_no": request.page_no,
            "page_size": request.page_size,
        }
    }
    logger.info(f"list knowledge base, {res}")
    return res


class File(BaseModel):
    filename: Optional[str] = Field(..., description="文件名")
    file_url: Optional[str] = Field(..., description="文件的url")
    file_type: Optional[str] = Field("file")


def add_file(filename, file_url, kb_id):
    tempdir = tempfile.gettempdir()
    # 下载文件到临时目录
    file_id = uuid.uuid4().hex
    work_dir = f"{tempdir}/{file_id}"
    os.makedirs(os.path.join(tempdir, file_id), exist_ok=True)

    kb_file = KBFileModel(
        kb_id=kb_id,
        file_id=file_id,
        file_url=file_url,
        title=filename,
        source_type=SourceTypeEnum.FILE.value,
        task_status={"global_status": TaskStatusEnum.PENDING.value},
        file_status=TaskStatusEnum.PENDING.value,
        doc_count=0,
        create_time=datetime.now(),
        modify_time=datetime.now(),
        deleted=0
    )
    kb_file_store = get_kb_file_store()
    kb_file_store.add_file(kb_file)

    local_file_path = os.path.join(tempdir, file_id, filename)
    download_utils.download_file(file_url, local_file_path)

    kb_file.file_status = TaskStatusEnum.RUNNING.value
    kb_file_store.update_file(kb_file)
    processor = DocumentProcessor(kb_id, file_id, work_dir, local_file_path, file_url)
    processor.process()

    kb_file.file_status = TaskStatusEnum.SUCCESS.value
    kb_file_store.update_file(kb_file)

    if os.path.exists(local_file_path):
        os.remove(local_file_path)


class AddFilesRequest(BaseModel):
    files: List[File] = Field(..., description="文件列表")
    kb_id: str = Field(..., description="知识库id")


@router.post("/add_files")
async def add_files(request: AddFilesRequest, background_tasks: BackgroundTasks):
    for file in request.files:
        filename = file.filename
        file_url = file.file_url

        background_tasks.add_task(
            add_file,
            filename=filename,
            file_url=file_url,
            kb_id=request.kb_id,
        )

    return {
        "code": 200,
        "msg": "success",
        "data": {}
    }


def add_web_url(url, kb_id):
    tempdir = tempfile.gettempdir()
    # 下载文件到临时目录
    file_id = uuid.uuid4().hex
    work_dir = f"{tempdir}/{file_id}"
    os.makedirs(os.path.join(tempdir, file_id), exist_ok=True)

    kb_file = KBFileModel(
        kb_id=kb_id,
        file_id=file_id,
        file_url=url,
        title="",
        source_type=SourceTypeEnum.FILE.value,
        task_status={"global_status": TaskStatusEnum.PENDING.value},
        file_status=TaskStatusEnum.PENDING.value,
        doc_count=0,
        create_time=datetime.now(),
        modify_time=datetime.now(),
        deleted=0
    )
    kb_file_store = get_kb_file_store()
    kb_file_store.add_file(kb_file)

    local_file_path = os.path.join(tempdir, file_id, f"{file_id}.md")
    markdown_content = crawl_utils.crawl(url)
    if not markdown_content:
        kb_file.file_status = TaskStatusEnum.FAILED.value
        kb_file_store.update_file(kb_file)
        return

    with open(local_file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    kb_file.file_status = TaskStatusEnum.RUNNING.value
    kb_file_store.update_file(kb_file)
    processor = DocumentProcessor(kb_id, file_id, work_dir, local_file_path, url)
    processor.process()

    kb_file.file_status = TaskStatusEnum.SUCCESS.value
    kb_file_store.update_file(kb_file)

    if os.path.exists(local_file_path):
        os.remove(local_file_path)


class AddWebUrlRequest(BaseModel):
    url: str = Field(..., description="url")
    kb_id: str = Field(..., description="知识库id")


@router.post("/add_web_url")
async def async_add_web_url(request: AddWebUrlRequest, background_tasks: BackgroundTasks):
    kb_id = request.kb_id
    url = request.url
    background_tasks.add_task(
        add_web_url,
        url, kb_id,
    )

    return {
        "code": 200,
        "msg": "success",
    }


class DeleteFileRequest(BaseModel):
    file_ids: List[str] = Field(..., description="文件id")
    kb_id: str = Field(..., description="知识库id")


@router.post("/delete_files")
async def delete_files(request: DeleteFileRequest):
    file_ids = request.file_ids
    kb_id = request.kb_id

    kb_file_store = get_kb_file_store()
    kb_file_store.delete_by_file_ids(kb_id, file_ids)

    vector_store = VectorStore()
    vector_store.delete_by_file_ids(kb_id, file_ids)

    return {
        "code": 200,
        "msg": "success",
        "data": {}
    }


class ListKBFilesRequest(BaseModel):
    kb_id: str
    page_no: Optional[int] = Field(1, description="page_no")
    page_size: Optional[int] = Field(10, description="page_size")


@router.post("/list_kb_files")
async def list_kb_files(request: ListKBFilesRequest):
    kb_id = request.kb_id
    page_no = request.page_no
    page_size = request.page_size
    kb_file_store = get_kb_file_store()
    records = kb_file_store.list_kb_files(kb_id, page_no, page_size)
    total = kb_file_store.count_kb_files(kb_id)
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "records": records,
            "page_no": page_no,
            "page_size": page_size,
        }
    }
