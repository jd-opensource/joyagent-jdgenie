import os
import re
from typing import List

from fastapi import UploadFile
from sqlmodel import select

from genie_tool.db.file_table import FileInfo
from genie_tool.db.db_engine import async_session_local
from genie_tool.util.log_util import timer


class _FileDB(object):
    def __init__(self):
        self._work_dir = os.getenv("FILE_SAVE_PATH", "file_db_dir")
        if not os.path.exists(self._work_dir):
            os.makedirs(self._work_dir)

    def _sanitize_filename(self, name: str) -> str:
        # 替换 Windows 非法字符：<>:"/\|?*
        return re.sub(r'[<>:"/\\|?*]', '_', name)

    async def save(self, file_name, content, scope) -> str:
        if "." in file_name:
            file_name = os.path.basename(file_name)
        else:
            file_name = f"{file_name}.txt"

        safe_scope = self._sanitize_filename(scope or "default")
        save_path = os.path.join(self._work_dir, safe_scope)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open(f"{save_path}/{file_name}", "w", encoding='utf-8') as f:
            f.write(content)
        return f"{save_path}/{file_name}"
    
    async def save_by_data(self, file: UploadFile) -> str:
        file_name = file.filename
        file_data = file.file.read()
        save_path = os.path.join(self._work_dir, file_name)
        with open(save_path, "wb") as f:
             f.write(file_data)
        return save_path


FileDB = _FileDB()


class FileInfoOp(object):

    @classmethod
    @timer()
    async def add_by_content(cls, filename: str, content: str, file_id: str, description: str = None,
                             request_id: str = None) -> FileInfo:
        file_path = await FileDB.save(filename, content, scope=request_id)
        file_info = FileInfo(
            file_id=file_id,
            filename=filename,
            file_path=file_path,
            description=description,
            file_size=os.path.getsize(file_path),
            status=1,
            request_id=request_id
        )
        return await cls.add(file_info)
    
    @staticmethod
    @timer()
    async def add_by_file(file: UploadFile, file_id: str, request_id: str = None) -> FileInfo:
        file_path = await FileDB.save_by_data(file)
        
        file_info = FileInfo(
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            description="",
            file_size=os.path.getsize(file_path),
            status=1,
            request_id=request_id
        )
        return await FileInfoOp.add(file_info)

    @staticmethod
    @timer()
    async def add(file_info: FileInfo) -> FileInfo:
        file_id = file_info.file_id
        f = await FileInfoOp.get_by_file_id(file_info.file_id)
        async with async_session_local() as session:
            if f:
                f.status = 1
                f.file_size = file_info.file_size
                session.add(f)
            else:
                session.add(file_info)
            await session.commit()
        return await FileInfoOp.get_by_file_id(file_id)

    @staticmethod
    @timer()
    async def get_by_file_id(file_id: str) -> FileInfo:
        async with async_session_local() as session:
            state = select(FileInfo).where(FileInfo.file_id == file_id)
            result = await session.execute(state)
            return result.scalars().one_or_none()

    @staticmethod
    @timer()
    async def get_by_file_ids(file_ids: List[str]) -> List[FileInfo]:
        async with async_session_local() as session:
            state = select(FileInfo).where(FileInfo.file_id.in_(file_ids))
            result = await session.execute(state)
            return result.scalars().all()

    @staticmethod
    @timer()
    async def get_by_request_id(request_id: str) -> List[FileInfo]:
        async with async_session_local() as session:
            state = select(FileInfo).where(FileInfo.request_id == request_id)
            result = await session.execute(state)
            return result.scalars().all()

def get_file_preview_url(file_id: str, file_name: str):
    return f"{os.getenv('FILE_SERVER_URL')}/preview/{file_id}/{file_name}"


def get_file_download_url(file_id: str, file_name: str):
    return f"{os.getenv('FILE_SERVER_URL')}/download/{file_id}/{file_name}"
