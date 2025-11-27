from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing_extensions import override

from .kb_store import KBStore
from .models.kb_model import KBModel

Base = declarative_base()


class KnowledgeBase(Base):
    __tablename__ = "t_knowledge_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kb_id = Column(String, nullable=False)
    kb_name = Column(String, nullable=True)
    kb_desc = Column(String, nullable=True)
    chunk_type = Column(String, nullable=True)
    chunk_size = Column(Integer, nullable=True)
    chunk_overlap_size = Column(Integer, nullable=True)
    deleted = Column(Integer, nullable=False, default=0)
    create_time = Column(DATETIME, nullable=False)
    modify_time = Column(DATETIME, nullable=False)
    creator = Column(String, nullable=True)


class KBStoreSQLite(KBStore):
    def __init__(self, engine):
        super().__init__()
        self._engine = engine
        self._session_factory = sessionmaker(bind=engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self._engine)

    @property
    def engine(self):
        return self._engine

    def _get_session(self) -> Session:
        """Get a new database session"""
        return self._session_factory()

    def _kb_model_to_orm(self, kb_model: KBModel) -> KnowledgeBase:
        """Convert KBModel to ORM entity"""
        return KnowledgeBase(
            kb_id=kb_model.kb_id,
            kb_name=kb_model.kb_name,
            kb_desc=kb_model.kb_desc,
            chunk_type=kb_model.chunk_type,
            chunk_size=kb_model.chunk_size,
            chunk_overlap_size=kb_model.chunk_overlap_size,
            deleted=kb_model.deleted,
            create_time=kb_model.create_time,
            modify_time=kb_model.modify_time or datetime.now(),
            creator=kb_model.creator
        )

    def _orm_to_kb_model(self, kb_orm: KnowledgeBase) -> KBModel:
        """Convert ORM entity to KBModel"""
        return KBModel(
            kb_id=kb_orm.kb_id,
            kb_name=kb_orm.kb_name,
            kb_desc=kb_orm.kb_desc,
            chunk_type=kb_orm.chunk_type,
            chunk_size=kb_orm.chunk_size,
            chunk_overlap_size=kb_orm.chunk_overlap_size,
            deleted=kb_orm.deleted,
            create_time=kb_orm.create_time,
            modify_time=kb_orm.modify_time,
            creator=kb_orm.creator
        )

    @override
    def create_kb(self, kb_model: KBModel) -> bool:
        """Create a new knowledge base"""
        session = self._get_session()
        try:
            # Check if knowledge base already exists
            existing_kb = session.query(KnowledgeBase).filter_by(
                kb_id=kb_model.kb_id,
                deleted=0
            ).first()

            if existing_kb:
                return False

            # Create new knowledge base
            kb_orm = self._kb_model_to_orm(kb_model)
            session.add(kb_orm)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @override
    def delete_kb(self, kb_model: KBModel) -> bool:
        """Soft delete a knowledge base"""
        session = self._get_session()
        try:
            # Find the knowledge base
            kb_orm = session.query(KnowledgeBase).filter_by(
                kb_id=kb_model.kb_id,
                deleted=0
            ).first()

            if not kb_orm:
                return False

            # Soft delete by setting deleted flag
            kb_orm.deleted = 1
            kb_orm.modify_time = datetime.now()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @override
    def update_kb(self, kb_model: KBModel) -> bool:
        """Update knowledge base metadata"""
        session = self._get_session()
        try:
            # Find the knowledge base
            kb_orm = session.query(KnowledgeBase).filter_by(
                kb_id=kb_model.kb_id,
                deleted=0
            ).first()

            if not kb_orm:
                return False

            # Update fields
            if kb_model.kb_name is not None:
                kb_orm.kb_name = kb_model.kb_name
            if kb_model.kb_desc is not None:
                kb_orm.kb_desc = kb_model.kb_desc
            if kb_model.chunk_type is not None:
                kb_orm.chunk_type = kb_model.chunk_type
            if kb_model.chunk_size is not None:
                kb_orm.chunk_size = kb_model.chunk_size
            if kb_model.chunk_overlap_size is not None:
                kb_orm.chunk_overlap_size = kb_model.chunk_overlap_size
            if kb_model.creator is not None:
                kb_orm.creator = kb_model.creator

            kb_orm.modify_time = datetime.now()
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @override
    def get_kbs(self, page_no: int, page_size: int) -> List[KBModel]:
        """Get knowledge bases with pagination"""
        session = self._get_session()
        try:
            # Query non-deleted knowledge bases with pagination
            query = session.query(KnowledgeBase).filter_by(deleted=0)

            # Apply pagination
            offset = (page_no - 1) * page_size
            kb_orms = query.offset(offset).limit(page_size).all()

            # Convert to KBModel list
            kb_models = [self._orm_to_kb_model(kb_orm) for kb_orm in kb_orms]
            return kb_models

        except Exception as e:
            raise e
        finally:
            session.close()
