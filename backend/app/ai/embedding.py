import hashlib
import os
import struct
from abc import ABC, abstractmethod

from openai import OpenAI

from app.config import Settings


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


class LocalEmbedder(Embedder):
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        from fastembed import TextEmbedding
        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [list(v) for v in self._model.embed(texts)]


class OpenAIEmbedder(Embedder):
    def __init__(self, settings: Settings):
        self._dim = settings.embedding_dim
        self._model = settings.embedding_model
        self._base_url = settings.openai_base_url
        self._api_key = settings.openai_api_key
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = OpenAI(base_url=self._base_url, api_key=self._api_key)
        return self._client

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._get_client().embeddings.create(
            model=self._model, input=texts, dimensions=self._dim
        )
        return [d.embedding for d in resp.data]


class FakeEmbedder(Embedder):
    def __init__(self, dim: int):
        self._dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._hash(text) for text in texts]

    def _hash(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vals = []
        for i in range(self._dim):
            chunk = h[(i * 4) % len(h):(i * 4) % len(h) + 4].ljust(4, b"\x00")
            vals.append(struct.unpack(">I", chunk)[0] / 4294967295.0)
        norm = sum(v * v for v in vals) ** 0.5 or 1.0
        return [v / norm for v in vals]
