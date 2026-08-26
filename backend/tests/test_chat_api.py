from fastapi.testclient import TestClient

from app.ai.embedding import FakeEmbedder
from app.ai.llm import FakeLLM
from app.db.vector_store import InMemoryVectorStore
from app.main import create_app


def _client(monkeypatch):
    monkeypatch.setattr("app.main.build_embedder", lambda s: FakeEmbedder(dim=8))
    monkeypatch.setattr("app.main.build_store", lambda s: InMemoryVectorStore())
    monkeypatch.setattr("app.main.build_llm", lambda s: FakeLLM("推荐沙发给你"))
    return TestClient(create_app())


def test_chat_endpoint_streams(monkeypatch):
    client = _client(monkeypatch)
    with client.stream("POST", "/chat", json={"conversation_id": "c1", "message": "有沙发吗"}) as resp:
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]
        body = "".join(resp.iter_text())
        assert "data:" in body
