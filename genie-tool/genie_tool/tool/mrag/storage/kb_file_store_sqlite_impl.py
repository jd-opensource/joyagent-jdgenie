from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from genie_tool.tool.mrag.storage.kb_file_store import KBFileStore
from genie_tool.tool.mrag.storage.models.kb_file_model import KBFileModel as KBFilePydanticModel

Base = declarative_base()


class KBFileSQLModel(Base):
    __tablename__ = "t_kb_file"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kb_id = Column(String, nullable=False)
    file_id = Column(String, nullable=False)
    file_url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    task_id = Column(String, nullable=True)
    file_ext = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    task_status = Column(JSON, nullable=True)
    file_status = Column(String, nullable=True)

    doc_count = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    modify_time = Column(DateTime, nullable=False)
    deleted = Column(Integer, nullable=False)
    creator = Column(String, nullable=True)

    def to_pydantic(self) -> KBFilePydanticModel:
        """Convert SQLAlchemy model to Pydantic model"""
        return KBFilePydanticModel(
            kb_id=self.kb_id,
            file_id=self.file_id,
            file_url=self.file_url,
            title=self.title,
            task_id=self.task_id,
            file_ext=self.file_ext,
            source_type=self.source_type,
            task_status=self.task_status,
            file_status=self.file_status,
            doc_count=self.doc_count,
            create_time=self.create_time,
            modify_time=self.modify_time,
            deleted=self.deleted
        )

    @staticmethod
    def from_pydantic(pydantic_model: KBFilePydanticModel) -> 'KBFileSQLModel':
        """Convert Pydantic model to SQLAlchemy model"""
        return KBFileSQLModel(
            kb_id=pydantic_model.kb_id,
            file_id=pydantic_model.file_id or "",
            file_url=pydantic_model.file_url or "",
            title=pydantic_model.title,
            task_id=pydantic_model.task_id,
            file_ext=pydantic_model.file_ext or "",
            source_type=pydantic_model.source_type or "",
            task_status=pydantic_model.task_status,
            file_status=pydantic_model.file_status,
            doc_count=pydantic_model.doc_count,
            create_time=pydantic_model.create_time or datetime.now(),
            modify_time=pydantic_model.modify_time or datetime.now(),
            deleted=pydantic_model.deleted,
            creator=pydantic_model.creator
        )


class KBFileSQLite(KBFileStore):
    __tablename__ = "t_kb_file"

    def __init__(self, engine):
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine)

        Base.metadata.create_all(self._engine)

    def _get_session(self) -> Session:
        return self._session_factory()

    def add_file(self, kb_file: KBFilePydanticModel) -> bool:
        """Add a new file to the knowledge base"""
        session = self._get_session()
        try:
            # Convert Pydantic model to SQLAlchemy model
            sql_model = KBFileSQLModel.from_pydantic(kb_file)
            session.add(sql_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_file(self, kb_file: KBFilePydanticModel) -> bool:
        """Delete a file from the knowledge base"""
        session = self._get_session()
        try:
            # Find the file by file_id and kb_id
            file_to_delete = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.file_id == kb_file.file_id,
                KBFileSQLModel.kb_id == kb_file.kb_id
            ).first()

            if file_to_delete:
                file_to_delete.deleted = 1
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_file(self, kb_file: KBFilePydanticModel) -> bool:
        """Update an existing file in the knowledge base"""
        session = self._get_session()
        try:
            # Find the file by file_id and kb_id
            file_to_update = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.file_id == kb_file.file_id,
                KBFileSQLModel.kb_id == kb_file.kb_id
            ).first()

            if file_to_update:
                # Update fields
                file_to_update.file_url = kb_file.file_url or file_to_update.file_url
                file_to_update.title = kb_file.title or file_to_update.title
                file_to_update.task_id = kb_file.task_id or file_to_update.task_id
                file_to_update.file_ext = kb_file.file_ext or file_to_update.file_ext
                file_to_update.source_type = kb_file.source_type or file_to_update.source_type
                file_to_update.task_status = kb_file.task_status or file_to_update.task_status
                file_to_update.file_status = kb_file.file_status or file_to_update.file_status
                file_to_update.doc_count = kb_file.doc_count or file_to_update.doc_count
                file_to_update.modify_time = datetime.now()
                file_to_update.creator = kb_file.creator or file_to_update.creator

                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_files(self, kb_id: str, page_no: int, page_size: int) -> List[KBFilePydanticModel]:
        """Get files from the knowledge base with pagination"""
        session = self._get_session()
        try:
            # Calculate offset for pagination
            offset = (page_no - 1) * page_size

            # Query files with pagination and filtering
            files = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.kb_id == kb_id,
                KBFileSQLModel.deleted == 0
            ).order_by(KBFileSQLModel.create_time.desc()).offset(offset).limit(page_size).all()

            # Convert SQLAlchemy models to Pydantic models
            return [file.to_pydantic() for file in files]
        except Exception as e:
            raise e
        finally:
            session.close()

    def delete_by_file_ids(self, kb_id: str, file_ids: List[str]):
        session = self._get_session()
        try:
            # Query files with pagination and filtering
            files = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.kb_id == kb_id,
                KBFileSQLModel.deleted == 0
            ).filter(KBFileSQLModel.file_id.in_(file_ids)).all()
            # Convert SQLAlchemy models to Pydantic models

            for file in files:
                file.deleted = 1
                file.modify_time = datetime.now()

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def list_kb_files(self, kb_id: str, page_no: int, page_size: int) -> List[KBFilePydanticModel]:
        session = self._get_session()
        try:
            # Calculate offset for pagination
            offset = (page_no - 1) * page_size

            # Query files with pagination and filtering
            files = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.kb_id == kb_id,
                KBFileSQLModel.deleted == 0
            ).order_by(KBFileSQLModel.create_time.desc()).offset(offset).limit(page_size).all()

            # Convert SQLAlchemy models to Pydantic models
            return [file.to_pydantic() for file in files]
        except Exception as e:
            raise e
        finally:
            session.close()

    def count_kb_files(self, kb_id: str) -> int:
        session = self._get_session()
        try:
            count = session.query(KBFileSQLModel).filter(
                KBFileSQLModel.kb_id == kb_id,
                KBFileSQLModel.deleted == 0
            ).count()
            return count
        except Exception as e:
            raise e
        finally:
            session.close()
