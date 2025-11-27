import mimetypes
import os
from urllib.parse import quote, unquote

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse, Response, FileResponse

from genie_tool.model.protocal import FileRequest, FileListRequest, FileUploadRequest, get_file_id
from genie_tool.util.middleware_util import RequestHandlerRoute
from genie_tool.db.file_table_op import FileInfoOp, get_file_preview_url, get_file_download_url
from genie_tool.util.log_util import logger

router = APIRouter(route_class=RequestHandlerRoute)


@router.post("/get_file")
async def get_file(
        body: FileRequest
):
    file_info = await FileInfoOp.get_by_file_id(file_id=body.file_id)
    if file_info:
        preview_url = get_file_preview_url(file_id=file_info.request_id, file_name=file_info.filename)
        download_url = get_file_download_url(file_id=file_info.request_id, file_name=file_info.filename)
        return JSONResponse(
            content={"ossUrl": download_url, "downloadUrl": download_url, "domainUrl": preview_url, "requestId": body.request_id,
                     "fileName": body.file_name})
    else:
        raise Exception("file not found")


@router.post("/upload_file")
async def upload_file(
        body: FileUploadRequest
):
    logger.info(f"upload file: {body}")
    file_info = await FileInfoOp.add_by_content(
        filename=body.file_name, content=body.content, file_id=body.file_id, description=body.description,
        request_id=body.request_id)
    preview_url = get_file_preview_url(file_id=file_info.request_id, file_name=file_info.filename)
    download_url = get_file_download_url(file_id=file_info.request_id, file_name=file_info.filename)
    return JSONResponse(content={"ossUrl": download_url, "downloadUrl": download_url, "domainUrl": preview_url, "fileSize": file_info.file_size})

@router.post("/upload_file_data")
async def upload_file_data(file: UploadFile = File(...), request_id: str = Form(alias="requestId")):
    file.filename = unquote(file.filename)
    file_id = get_file_id(request_id, file.filename)
    file_info = await FileInfoOp.add_by_file(file=file, file_id=file_id, request_id=request_id)
    preview_url = get_file_preview_url(file_id=file_info.request_id, file_name=file_info.filename)
    download_url = get_file_download_url(file_id=file_info.request_id, file_name=file_info.filename)
    return JSONResponse(content={"downloadUrl": download_url, "domainUrl": preview_url, "fileSize": file_info.file_size})


@router.post("/get_file_list")
async def get_file_list(body: FileListRequest):
    if not body.filters:
        file_infos = await FileInfoOp.get_by_request_id(body.request_id)
    else:
        file_infos = await FileInfoOp.get_by_file_ids(file_ids=[f.file_id for f in body.filters])
    if not file_infos:
         return JSONResponse(content={"results": [], "totalSize": 0})
    total_size = sum([f.file_size for f in file_infos])
    results = []
    for file_info in file_infos:
        preview_url = get_file_preview_url(file_id=file_info.request_id, file_name=file_info.filename)
        download_url = get_file_download_url(file_id=file_info.request_id, file_name=file_info.filename)
        results.append({
            "ossUrl": download_url,
            "downloadUrl": download_url, "domainUrl": preview_url,
            "requestId": file_info.request_id, "fileName": file_info.filename
        })
    return JSONResponse(content={"results": results, "totalSize": total_size})


@router.get("/download/{file_id}/{file_name}")
async def download_file(file_id: str, file_name: str):
    # TODO 目前 file_id 实际上是 request_id，后续统一修改
    file_id = get_file_id(file_id, file_name)
    file_info = await FileInfoOp.get_by_file_id(file_id=file_id)
    if not file_info or not os.path.exists(file_info.file_path):
        return Response(content="File not found", status_code=404)
    return FileResponse(file_info.file_path, filename=os.path.basename(file_name))


@router.get("/preview/{file_id}/{file_name}")
async def preview_file(file_id: str, file_name: str):
    # TODO 目前 file_id 实际上是 request_id，后续统一修改
    file_id = get_file_id(file_id, file_name)
    file_info = await FileInfoOp.get_by_file_id(file_id=file_id)
    if not file_info or not os.path.exists(file_info.file_path):
        return Response(content="File not found", status_code=404)

    disposition = "inline"
    if file_name.endswith(".md"):
        content_type = "text/markdown"
    else:
        content_type, _ = mimetypes.guess_type(file_name)
    if not content_type:
        content_type = "application/octet-stream"
        disposition = "attachment"

    encoded_file_name = quote(file_name)

    return FileResponse(
        file_info.file_path,
        filename=os.path.basename(file_name),
        media_type=content_type,
        headers={
            "Content-Disposition": f"{disposition}; filename=\"{encoded_file_name}\"; filename*=UTF-8''{encoded_file_name}",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

