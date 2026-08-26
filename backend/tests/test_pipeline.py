from app.ai.embedding import FakeEmbedder
from app.db.vector_store import InMemoryVectorStore
from app.rag.ingestion.pipeline import IngestionPipeline


def test_ingest_returns_chunk_count():
    pipe = IngestionPipeline(InMemoryVectorStore(), FakeEmbedder(dim=8))
    n = pipe.ingest("正文内容", {"doc_id": "d1", "source_type": "text", "title": "T"})
    assert n == 1


def test_ingest_with_attributes():
    pipe = IngestionPipeline(InMemoryVectorStore(), FakeEmbedder(dim=8))
    n = pipe.ingest("正文", {"doc_id": "d1", "source_type": "text", "title": "T",
                             "attributes": {"材质": "布艺"}})
    assert n == 2


def test_ingest_injects_title_into_chunks():
    store = InMemoryVectorStore()
    pipe = IngestionPipeline(store, FakeEmbedder(dim=8))
    pipe.ingest("正文内容", {"doc_id": "d1", "source_type": "text", "title": "北欧沙发"})
    assert all("title" in fields for fields in store._fields.values())
