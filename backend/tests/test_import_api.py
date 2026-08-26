from fastapi.testclient import TestClient

from app.ai.embedding import FakeEmbedder
from app.ai.llm import FakeLLM
from app.db.vector_store import InMemoryVectorStore
from app.main import create_app


def _client(monkeypatch):
    monkeypatch.setattr("app.main.build_embedder", lambda s: FakeEmbedder(dim=8))
    monkeypatch.setattr("app.main.build_store", lambda s: InMemoryVectorStore())
    monkeypatch.setattr("app.main.build_llm", lambda s: FakeLLM("x"))
    monkeypatch.setattr("app.main.build_image_embedder", lambda: None)
    return TestClient(create_app())


def test_import_endpoint(monkeypatch):
    client = _client(monkeypatch)
    resp = client.post("/import", json={"products": [
        {"title": "测试商品", "content": "这是商品描述", "price": 99,
         "category": "测试", "brand": "测试牌", "sku": "SKU001"}
    ]})
    assert resp.status_code == 200
    assert resp.json()["imported"] == 1


def test_import_multiple(monkeypatch):
    client = _client(monkeypatch)
    resp = client.post("/import", json={"products": [
        {"title": "A", "content": "描述A", "sku": "A1"},
        {"title": "B", "content": "描述B", "sku": "B1"},
        {"title": "C", "content": "描述C", "sku": "C1"},
    ]})
    assert resp.json()["imported"] == 3
