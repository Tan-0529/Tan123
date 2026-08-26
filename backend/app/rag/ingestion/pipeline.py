from app.ai.embedding import Embedder
from app.db.vector_store import VectorStore
from app.rag.ingestion.chunker import chunk_document
from app.rag.ingestion.parsers import get_parser


class IngestionPipeline:
    def __init__(self, store: VectorStore, embedder: Embedder):
        self._store = store
        self._embedder = embedder

    def ingest(self, raw: str, meta: dict) -> int:
        source_type = meta.get("source_type", "text")
        doc = get_parser(source_type).parse(raw, meta)
        chunks = chunk_document(doc)
        if not chunks:
            return 0
        vecs = self._embedder.embed([c.text for c in chunks])
        for chunk, vec in zip(chunks, vecs):
            chunk.metadata["vector"] = vec
        self._store.insert(chunks)
        return len(chunks)
