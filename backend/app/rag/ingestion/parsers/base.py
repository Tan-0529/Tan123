from abc import ABC, abstractmethod

from app.models.document import Document


class Parser(ABC):
    @abstractmethod
    def parse(self, raw: str, meta: dict) -> Document: ...
