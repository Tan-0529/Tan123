import base64
import os
import tempfile

from fastembed import ImageEmbedding


class ImageEmbedder:
    def __init__(self, model_name: str = "Qdrant/clip-ViT-B-32-vision"):
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        self._model = ImageEmbedding(model_name=model_name)

    @property
    def dim(self) -> int:
        return self._model.embedding_size

    def embed_url(self, url: str) -> list[float]:
        return self.embed_paths([url])[0]

    def embed_base64(self, b64: str) -> list[float]:
        data = base64.b64decode(b64)
        suffix = ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(data)
            path = f.name
        try:
            return self.embed_paths([path])[0]
        finally:
            os.unlink(path)

    def embed_paths(self, paths: list[str]) -> list[list[float]]:
        return [list(v) for v in self._model.embed(paths)]
