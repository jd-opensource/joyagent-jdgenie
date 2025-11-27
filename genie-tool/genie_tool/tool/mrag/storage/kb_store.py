from abc import abstractmethod, ABC
from typing import List

from .models.kb_model import KBModel


class KBStore(ABC):

    @abstractmethod
    def create_kb(self, kb_model: KBModel) -> bool:
        pass

    @abstractmethod
    def delete_kb(self, kb_model: KBModel) -> bool:
        pass

    @abstractmethod
    def update_kb(self, kb_model: KBModel) -> bool:
        pass

    @abstractmethod
    def get_kbs(self, page_no: int, page_size: int) -> List[KBModel]:
        pass
