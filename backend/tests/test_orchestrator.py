import pytest

from app.ai.embedding import FakeEmbedder
from app.ai.llm import FakeLLM
from app.core.memory import InMemoryMemory
from app.core.orchestrator import Orchestrator
from app.db.vector_store import InMemoryVectorStore
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
