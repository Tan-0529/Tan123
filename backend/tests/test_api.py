from fastapi.testclient import TestClient

from app.ai.embedding import FakeEmbedder
from app.db.vector_store import InMemoryVectorStore
from app.main import create_app


def _client(monkeypatch):
    monkeypatch.setattr("app.main.build_embedder", lambda s: FakeEmbedder(dim=8))
    monkeypatch.setattr("app.main.build_store", lambda s: InMemoryVectorStore())
    return TestClient(create_app())


def test_ingest_endpoint(monkeypatch):
    client = _client(monkeypatch)
    resp = client.post("/ingest", json={"doc_id": "d1", "source_type": "text",
                                        "title": "T", "content": "内容"})
    assert resp.status_code == 200
    assert resp.json()["chunks"] >= 1


def test_search_endpoint(monkeypatch):
    client = _client(monkeypatch)
    client.post("/ingest", json={"doc_id": "d1", "source_type": "text",
                                 "title": "T", "content": "布艺沙发"})
    resp = client.post("/search", json={"query": "沙发", "top_k": 1})
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1
