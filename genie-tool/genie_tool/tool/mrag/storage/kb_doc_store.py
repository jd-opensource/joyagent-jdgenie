from abc import abstractmethod, ABC
from typing import List

from .models.kb_doc_model import KBDocModel


class KBDocStore(ABC):

    @abstractmethod
    def add_doc(self, kb_doc: KBDocModel) -> bool:
        pass

    @abstractmethod
    def delete_doc(self, kb_doc: KBDocModel) -> bool:
        pass

    @abstractmethod
    def update_doc(self, kb_doc: KBDocModel) -> bool:
        pass

    @abstractmethod
    def get_docs(self, file_id: str, page_no: int, page_size: int) -> List[KBDocModel]:
        pass
