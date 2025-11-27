import hashlib
import os
import pathlib
from urllib import request
from urllib.parse import quote
from urllib.parse import unquote

import boto3
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .logger_utils import logger

router = APIRouter(prefix="/storage", tags=["OSS"])


def get_file_extension(file_path):
    # 普通后缀处理
    extension = pathlib.Path(file_path).suffix

    # 加密链接处理
    if "?" in extension:
        extension = extension.split("?")[0]

    return extension


def upload_oss(file_path, dir_, is_delete=True):
    # bucket_name, access_key, secret_key, endpoint,
    bucket = os.getenv("S3_BUCKET_NAME")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    endpoint = os.getenv("S3_ENDPOINT")
    return upload_s3(file_path, bucket, access_key, secret_key, endpoint, dir_, is_delete)


def upload_s3(file_path, bucket_name, access_key, secret_key, endpoint, dir_, is_delete=True):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint
        )
        oss_name = dir_ + "/" + os.path.basename(file_path)
        # 上传文件
        resp = s3.put_object(Bucket=bucket_name, Key=oss_name, Body=open(file_path, 'rb').read(),
                             StorageClass='STANDARD')
        return_code = resp["ResponseMetadata"]["HTTPStatusCode"]
        if return_code == 200:
            upload_url = create_permanent_download_url(bucket_name, oss_name)
            # s3生成链接
            presigned_url = s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': oss_name
                },
                ExpiresIn=3600 * 24 * 365
            )
            return True, upload_url, presigned_url
        return False, None
        # 获得外链
    finally:
        if is_delete:
            # 检查文件是否存在
            if file_path is not None and os.path.isfile(file_path):
                # 存在，则删除
                os.remove(file_path)


def generate_secure_token(bucket_name, object_key, secret_key):
    """
    为对象生成安全令牌，用于永久访问链接

    参数:
        bucket_name: S3存储桶名称
        object_key: 对象的键（路径）
        secret_key: 用于签名的密钥

    返回:
        安全令牌
    """
    # 组合信息并加盐
    data = f"{bucket_name}:{object_key}:{secret_key}"
    # 使用SHA-256生成哈希
    token = hashlib.sha256(data.encode()).hexdigest()
    return token


def create_permanent_download_url(bucket_name, object_key, access_key=None, secret_key=None):
    """
    创建对象的永久下载链接（通过服务器代理访问）

    参数:
        bucket_name: S3存储桶名称
        object_key: 对象的键（路径）
        access_key: S3访问密钥（可选，默认使用环境变量）
        secret_key: S3秘密密钥（可选，默认使用环境变量）

    返回:
        永久下载链接
    """
    if not secret_key:
        secret_key = os.getenv("S3_SECRET_KEY")

    # 生成安全令牌
    token = generate_secure_token(bucket_name, object_key, secret_key)

    # 构建API端点URL（需要在服务器端实现对应的API）
    api_base_url = os.getenv("OSS_SERVER_BASE_URL", "http://127.0.0.1:7861/oss")
    permanent_url = f"{api_base_url}/download/{bucket_name}/{quote(object_key)}/{token}"

    return permanent_url


def download(file_url, save_path):
    logger.info(file_url)
    logger.info("文件开始下载... 来源:{}".format(file_url))
    # 获取文件扩展名
    extension = get_file_extension(file_url)
    file_name = save_path + extension
    try:
        request.urlretrieve(file_url, file_name)
        logger.info("文件下载完成,地址:{}".format(save_path))
        return "success", save_path
    except:
        logger.info("文件下载失败!")
        return "failed", ""


def verify_token(bucket_name, object_key, token):
    """验证访问令牌是否有效"""
    secret_key = os.getenv("S3_SECRET_KEY")
    expected_token = generate_secure_token(bucket_name, object_key, secret_key)
    return token == expected_token


@router.get("/download/{bucket_name}/{object_key:path}/{token}")
def download_file(bucket_name: str, object_key: str, token: str):
    """
    通过安全令牌提供S3对象的永久下载

    参数:
        bucket_name: S3存储桶名称
        object_key: 对象的键（路径，URL编码）
        token: 安全访问令牌
    """
    try:
        # URL解码对象键
        object_key = unquote(object_key)

        # 验证令牌
        if not verify_token(bucket_name, object_key, token):
            logger.warning(f"无效的访问令牌: {token} 用于 {bucket_name}/{object_key}")
            raise HTTPException(status_code=403, detail="无效的访问令牌")

        # 获取S3客户端
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            endpoint_url=os.getenv("S3_ENDPOINT")
        )

        # 检查对象是否存在
        try:
            response = s3.head_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            logger.error(f"对象不存在或无法访问: {bucket_name}/{object_key}, 错误: {str(e)}")
            raise HTTPException(status_code=404, detail="文件不存在或无法访问")

        # 获取对象内容
        obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        content_type = obj.get('ContentType', 'application/octet-stream')

        # 获取文件名（从对象键中提取）
        filename = os.path.basename(object_key)

        # 创建流式响应
        def iterfile():
            yield from obj['Body'].iter_chunks()

        # 返回流式响应
        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载文件时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


def upload_local_storage(file_path: str, file_id: str=None):
    import mimetypes
    import requests
    import uuid

    if file_id is None:
        file_id = uuid.uuid4().hex

    def get_content_type(file_path):
        """根据文件扩展名获取 content_type"""
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            # 为常见文件类型提供默认值
            ext = os.path.splitext(file_path)[1].lower()
            content_type_map = {
                '.pdf': 'application/pdf',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.doc': 'application/msword',
                '.txt': 'text/plain',
                '.md': 'text/markdown',
                '.json': 'application/json',
                '.xml': 'application/xml',
                '.csv': 'text/csv',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.xls': 'application/vnd.ms-excel',
                '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                '.ppt': 'application/vnd.ms-powerpoint',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
            }
            content_type = content_type_map.get(ext, 'application/octet-stream')
        return content_type

    def upload_local_path(local_file_path: str):
        file_name = os.path.basename(local_file_path)
        file_name = f"{file_id}_{file_name}"
        content_type = get_content_type(local_file_path)

        with open(local_file_path, "rb") as f:
            data = {"requestId": uuid.uuid4().hex}

            response = requests.post(
                "http://127.0.0.1:1601/v1/file_tool/upload_file_data",
                files={
                    "file": (file_name, f, content_type)
                },
                data=data
            )
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")

        return response.json()['downloadUrl']

    return upload_local_path(file_path)
