import os

from sqlalchemy import create_engine

from .kb_doc_store import KBDocStore
from .kb_file_store import KBFileStore
from .kb_store import KBStore

_sqlite_engine = None

store_type = os.getenv("STORE_TYPE", "sqlite")

if store_type == "sqlite":
    local_path = os.getenv("SQLITE_PATH", "kb_file.db")
    _sqlite_engine = create_engine(f"sqlite:///{local_path}")

def get_kb_file_store() -> KBFileStore:
    global _sqlite_engine, store_type
    if store_type == "sqlite":
        from .kb_file_store_sqlite_impl import KBFileSQLite
        return KBFileSQLite(_sqlite_engine)
    else:
        raise Exception("Unknown store type")


def get_kb_store() -> KBStore:
    global _sqlite_engine, store_type
    if store_type == "sqlite":
        from .kb_store_sqlite_impl import KBStoreSQLite
        return KBStoreSQLite(_sqlite_engine)
    else:
        raise Exception("Unknown store type")


def get_kb_doc_store() -> KBDocStore:
    global _sqlite_engine, store_type
    if store_type == "sqlite":
        from .kb_doc_store_sqlite_impl import KBDocSQLite
        return KBDocSQLite(_sqlite_engine)
    else:
        raise Exception("Unknown store type")