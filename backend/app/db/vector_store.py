from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.chunk import Chunk


@dataclass
class SearchHit:
    id: str
    score: float
    fields: dict = field(default_factory=dict)


class VectorStore(ABC):
    @abstractmethod
    def insert(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    def search(self, vector: list[float], top_k: int = 50,
               expr: str | None = None, field: str = "vector") -> list[SearchHit]: ...

    @abstractmethod
    def close(self) -> None: ...


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self._vecs: dict[str, list[float]] = {}
        self._vision_vecs: dict[str, list[float]] = {}
        self._fields: dict[str, dict] = {}

    def insert(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self._vecs[c.id] = c.metadata.get("vector", [0.0])
            self._vision_vecs[c.id] = c.metadata.get("vision_embedding", [0.0])
            self._fields[c.id] = {"text": c.text, "priority": c.priority, **c.metadata}

    def search(self, vector, top_k=50, expr=None, field: str = "vector"):
        allowed = self._eval_expr(expr)
        scored = []
        for cid, fields in self._fields.items():
            if not allowed(cid, fields):
                continue
            vecs = self._vision_vecs if field == "vision_embedding" else self._vecs
            vec = vecs.get(cid, [0.0])
            score = sum(a * b for a, b in zip(vector, vec))
            scored.append(SearchHit(id=cid, score=score, fields=fields))
        scored.sort(key=lambda h: -h.score)
        return scored[:top_k]

    def _eval_expr(self, expr):
        if not expr:
            return lambda cid, f: True
        return lambda cid, f: self._match(f, expr)

    @staticmethod
    def _match(fields, expr):
        parts = [p.strip() for p in expr.split("<=")]
        if len(parts) == 2:
            return float(fields[parts[0]]) <= float(parts[1])
        return True

    def close(self) -> None:
        pass
