from app.ai.embedding import FakeEmbedder
from app.db.vector_store import InMemoryVectorStore
from app.models.chunk import Chunk
from app.rag.retriever import Retriever


def _make_retriever():
    store = InMemoryVectorStore()
    return Retriever(store, FakeEmbedder(dim=8)), store


def test_retrieve_returns_results():
    r, store = _make_retriever()
    store.insert([Chunk(id="c1", doc_id="d1", text="布艺沙发", chunk_type="description",
                        metadata={"price": 1999})])
    results = r.retrieve("沙发", top_k=1)
    assert len(results) == 1
    assert "text" in results[0]


def test_build_expr_from_filters():
    r, _ = _make_retriever()
    expr = r._build_expr({"category": "沙发", "max_price": 5000})
    assert "沙发" in expr and "5000" in expr


def test_retrieve_empty_expr_when_no_filters():
    r, _ = _make_retriever()
    assert r._build_expr(None) is None
