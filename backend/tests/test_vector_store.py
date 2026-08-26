from app.db.vector_store import InMemoryVectorStore
from app.models.chunk import Chunk


def _chunk(cid, text, priority=5, **meta):
    return Chunk(id=cid, doc_id="d1", text=text, chunk_type="description",
                 priority=priority, metadata=meta)


def test_insert_and_search():
    store = InMemoryVectorStore()
    store.insert([_chunk("c1", "布艺沙发", price=1999), _chunk("c2", "实木餐桌", price=2999)])
    hits = store.search([0.0, 1.0], top_k=1, expr=None)
    assert hits[0].id in {"c1", "c2"}


def test_search_respects_top_k():
    store = InMemoryVectorStore()
    store.insert([_chunk(f"c{i}", "t") for i in range(5)])
    assert len(store.search([0.0], top_k=3, expr=None)) == 3


def test_inmemory_filter_expr():
    store = InMemoryVectorStore()
    store.insert([_chunk("c1", "a", price=100), _chunk("c2", "b", price=500)])
    hits = store.search([0.0], top_k=10, expr="price <= 200")
    assert [h.id for h in hits] == ["c1"]
