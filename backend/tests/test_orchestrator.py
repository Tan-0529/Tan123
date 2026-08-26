import pytest

from app.ai.embedding import FakeEmbedder
from app.ai.llm import FakeLLM
from app.core.memory import InMemoryMemory
from app.core.orchestrator import Orchestrator, _extract_cards
from app.db.vector_store import InMemoryVectorStore
from app.models.chunk import Chunk
from app.rag.retriever import Retriever


@pytest.mark.asyncio
async def test_stream_chat_emits_delta_and_done():
    store = InMemoryVectorStore()
    retriever = Retriever(store, FakeEmbedder(dim=8))
    orch = Orchestrator(retriever, FakeLLM("这是推荐"), InMemoryMemory())
    events = [e async for e in orch.stream_chat("c1", "有沙发吗")]
    kinds = [e["event"] for e in events]
    assert "delta" in kinds
    assert kinds[-1] == "done"


@pytest.mark.asyncio
async def test_stream_chat_saves_history():
    mem = InMemoryMemory()
    orch = Orchestrator(Retriever(InMemoryVectorStore(), FakeEmbedder(dim=8)),
                        FakeLLM("好"), mem)
    async for _ in orch.stream_chat("c1", "你好"):
        pass
    assert len(mem.get_history("c1")) == 2


def test_extract_cards_deduplicates_by_sku():
    results = [
        {"text": "材质: 布艺", "score": 0.9,
         "metadata": {"sku": "S1", "title": "北欧沙发", "price": 3999,
                      "rating": 4.8, "image_url": "http://x/1.jpg",
                      "product_url": "http://x/p/1"}},
        {"text": "颜色: 米色", "score": 0.8,
         "metadata": {"sku": "S1", "title": "北欧沙发", "price": 3999,
                      "rating": 4.8, "image_url": "http://x/1.jpg",
                      "product_url": "http://x/p/1"}},
    ]
    cards = _extract_cards(results)
    assert len(cards) == 1
    assert cards[0]["sku"] == "S1"
    assert cards[0]["price"] == 3999


@pytest.mark.asyncio
async def test_stream_chat_emits_card_events():
    store = InMemoryVectorStore()
    store.insert([Chunk(id="c1", doc_id="d1", text="布艺沙发", chunk_type="description",
                        metadata={"sku": "SKU001", "title": "北欧沙发", "price": 3999,
                                  "rating": 4.8, "image_url": "http://x/1.jpg",
                                  "product_url": "http://x/p/1"})])
    orch = Orchestrator(Retriever(store, FakeEmbedder(dim=8)),
                        FakeLLM("推荐"), InMemoryMemory())
    events = [e async for e in orch.stream_chat("c1", "沙发")]
    cards = [e for e in events if e["event"] == "card"]
    assert len(cards) == 1
    assert cards[0]["data"]["sku"] == "SKU001"

