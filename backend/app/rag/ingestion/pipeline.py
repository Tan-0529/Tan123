from app.ai.embedding import Embedder
from app.db.vector_store import VectorStore
from app.rag.ingestion.chunker import chunk_document
from app.rag.ingestion.parsers import get_parser


class IngestionPipeline:
    def __init__(self, store: VectorStore, embedder: Embedder, image_embedder=None):
        self._store = store
        self._embedder = embedder
        self._image_embedder = image_embedder

    def ingest(self, raw: str, meta: dict) -> int:
        source_type = meta.get("source_type", "text")
        doc = get_parser(source_type).parse(raw, meta)
        chunks = chunk_document(doc)
        if not chunks:
            return 0
        for chunk in chunks:
            chunk.metadata["title"] = doc.title

        vision_vec = None
        image_url = doc.metadata.get("image_url", "")
        if image_url and self._image_embedder is not None:
            try:
                vision_vec = self._image_embedder.embed_url(image_url)
            except Exception:
                vision_vec = None

        vecs = self._embedder.embed([c.text for c in chunks])
        for chunk, vec in zip(chunks, vecs):
            chunk.metadata["vector"] = vec
            if vision_vec is not None:
                chunk.metadata["vision_embedding"] = vision_vec
        self._store.insert(chunks)
        return len(chunks)
