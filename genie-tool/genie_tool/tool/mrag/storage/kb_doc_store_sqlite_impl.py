from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from genie_tool.tool.mrag.storage.kb_doc_store import KBDocStore
from genie_tool.tool.mrag.storage.models.kb_doc_model import KBDocModel as KBDocPydanticModel

Base = declarative_base()


class KBDocSQLModel(Base):
    __tablename__ = "t_kb_doc"
    id = Column(Integer, primary_key=True, autoincrement=True)
    kb_id = Column(String, nullable=False)
    doc_id = Column(String, nullable=False)
    text = Column(String, nullable=False)
    chunk_type = Column(String, nullable=False)
    file_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    parent_id = Column(String, nullable=False)

    deleted = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    modify_time = Column(DateTime, nullable=False)
    creator = Column(String, nullable=True)
    modifier = Column(String, nullable=True)

    def to_pydantic(self) -> KBDocPydanticModel:
        """Convert SQLAlchemy model to Pydantic model"""
        return KBDocPydanticModel(
            kb_id=self.kb_id,
            doc_id=self.doc_id,
            text=self.text,
            chunk_type=self.chunk_type,
            file_id=self.file_id,
            title=self.title,
            file_url=self.file_url,
            parent_id=self.parent_id,
            deleted=self.deleted,
            create_time=self.create_time.isoformat() if self.create_time else None,
            modify_time=self.modify_time.isoformat() if self.modify_time else None,
            creator=self.creator,
            modifier=self.modifier
        )

    @staticmethod
    def from_pydantic(pydantic_model: KBDocPydanticModel) -> 'KBDocSQLModel':
        """Convert Pydantic model to SQLAlchemy model"""
        return KBDocSQLModel(
            kb_id=pydantic_model.kb_id or "",
            doc_id=pydantic_model.doc_id or "",
            text=pydantic_model.text or "",
            chunk_type=pydantic_model.chunk_type or "",
            file_id=pydantic_model.file_id or "",
            title=pydantic_model.title or "",
            file_url=pydantic_model.file_url or "",
            parent_id=pydantic_model.parent_id or "",
            deleted=pydantic_model.deleted or 0,
            create_time=datetime.fromisoformat(pydantic_model.create_time) if pydantic_model.create_time else datetime.now(),
            modify_time=datetime.fromisoformat(pydantic_model.modify_time) if pydantic_model.modify_time else datetime.now(),
            creator=pydantic_model.creator,
            modifier=pydantic_model.modifier
        )


class KBDocSQLite(KBDocStore):
    __tablename__ = "t_kb_doc"

    def __init__(self, engine):
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine)

        Base.metadata.create_all(self._engine)

    def _get_session(self) -> Session:
        return self._session_factory()

    def add_doc(self, kb_doc: KBDocPydanticModel) -> bool:
        """Add a new document to the knowledge base"""
        session = self._get_session()
        try:
            # Convert Pydantic model to SQLAlchemy model
            sql_model = KBDocSQLModel.from_pydantic(kb_doc)
            session.add(sql_model)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def delete_doc(self, kb_doc: KBDocPydanticModel) -> bool:
        """Delete a document from the knowledge base"""
        session = self._get_session()
        try:
            # Find the document by doc_id and kb_id
            doc_to_delete = session.query(KBDocSQLModel).filter(
                KBDocSQLModel.doc_id == kb_doc.doc_id,
                KBDocSQLModel.kb_id == kb_doc.kb_id
            ).first()
            
            if doc_to_delete:
                session.delete(doc_to_delete)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_doc(self, kb_doc: KBDocPydanticModel) -> bool:
        """Update an existing document in the knowledge base"""
        session = self._get_session()
        try:
            # Find the document by doc_id and kb_id
            doc_to_update = session.query(KBDocSQLModel).filter(
                KBDocSQLModel.doc_id == kb_doc.doc_id,
                KBDocSQLModel.kb_id == kb_doc.kb_id
            ).first()
            
            if doc_to_update:
                # Update fields
                doc_to_update.text = kb_doc.text or doc_to_update.text
                doc_to_update.chunk_type = kb_doc.chunk_type or doc_to_update.chunk_type
                doc_to_update.file_id = kb_doc.file_id or doc_to_update.file_id
                doc_to_update.title = kb_doc.title or doc_to_update.title
                doc_to_update.file_url = kb_doc.file_url or doc_to_update.file_url
                doc_to_update.parent_id = kb_doc.parent_id or doc_to_update.parent_id
                doc_to_update.modify_time = datetime.now()
                doc_to_update.modifier = kb_doc.modifier or doc_to_update.modifier
                
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_docs(self, file_id: str, page_no: int, page_size: int) -> List[KBDocPydanticModel]:
        """Get documents from the knowledge base with pagination"""
        session = self._get_session()
        try:
            # Calculate offset for pagination
            offset = (page_no - 1) * page_size
            
            # Query documents with pagination and filtering
            docs = session.query(KBDocSQLModel).filter(
                KBDocSQLModel.file_id == file_id,
                KBDocSQLModel.deleted == 0
            ).order_by(KBDocSQLModel.create_time.desc()).offset(offset).limit(page_size).all()
            
            # Convert SQLAlchemy models to Pydantic models
            return [doc.to_pydantic() for doc in docs]
        except Exception as e:
            raise e
        finally:
            session.close()
