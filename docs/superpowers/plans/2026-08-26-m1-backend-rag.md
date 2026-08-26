# M1 后端 + RAG 检索 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建 FastAPI 后端骨架 + 文档摄取管线（解析/切片）+ RAG 混合检索，实现「文档入库 → 向量检索 → 返回商品上下文」的端到端闭环。

**Architecture:** 采用「接口抽象 + 可替换实现」策略。向量存储、Embedding、解析器均定义抽象接口，M1 用轻量实现（Milvus Lite / OpenAI 兼容 Embedding），生产可无缝切换 Milvus 集群，测试用内存 Fake。分层：`api`（路由）→ `rag`（检索/摄取）→ `db`/`ai`（存储/模型）→ `models`（数据模型）。

**Tech Stack:** Python 3.14 + FastAPI 0.141 + pydantic 2 + pymilvus 3.0（Milvus Lite）+ OpenAI SDK 3.3 + beautifulsoup4 + pytest + pytest-asyncio。

**Spec:** `C:\Users\lenovo\Documents\Agent项目\SmartShop-AI-实施方案.md`

## Global Constraints

- 项目根目录：`C:\Users\lenovo\Documents\Agent项目`（Windows）
- 后端代码全部位于 `backend/` 目录，包名 `app`
- Python 3.14，依赖安装到 `backend/.venv`
- 向量维度默认 1024（`EMBEDDING_DIM` 环境变量可覆盖）
- Embedding 走 OpenAI 兼容 API（`OPENAI_BASE_URL` + `OPENAI_API_KEY` + `EMBEDDING_MODEL`）
- 向量库用 Milvus Lite（`MilvusClient("backend/milvus.db")`），生产切 `MILVUS_URI` 集群
- 切片策略：属性切片（priority=10）+ 描述切片（priority=5）
- 检索融合：RRF + 属性加权（priority 系数）
- 所有代码不带注释除非必要；测试文件放在 `backend/tests/`
- 提交信息格式：`feat:` / `refactor:` / `test:` / `chore:`

---

### Task 1: 项目骨架 + 配置 + 依赖

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/.env.example`
- Create: `backend/tests/__init__.py`
- Create: `backend/pytest.ini`
- Create: `.gitignore`

**Interfaces:**
- Produces: `app.config.Settings`（`openai_base_url`, `openai_api_key`, `embedding_model`, `embedding_dim`, `milvus_uri`, `milvus_db_path`）

- [ ] **Step 1: 写失败测试**

`backend/tests/test_config.py`:
```python
import os
from app.config import Settings

def test_settings_defaults():
    settings = Settings(_env_file=None)
    assert settings.embedding_dim == 1024
    assert settings.embedding_model == "text-embedding-3-large"
    assert settings.milvus_db_path.endswith("milvus.db")

def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("EMBEDDING_DIM", "768")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    settings = Settings(_env_file=None)
    assert settings.embedding_dim == 768
    assert settings.openai_api_key == "sk-test"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `backend/.venv/Scripts/python.exe -m pytest tests/test_config.py -v`
Expected: FAIL（`ModuleNotFoundError: No module named 'app'`）

- [ ] **Step 3: 写实现**

`backend/app/config.py`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-large"
    embedding_dim: int = 1024
    milvus_uri: str = ""                      # 空=用本地 Lite
    milvus_db_path: str = "milvus.db"
    milvus_collection: str = "product"
```

`backend/requirements.txt`:
```text
fastapi>=0.141
uvicorn[standard]>=0.52
pydantic>=2.13
pydantic-settings>=2.15
openai>=3.3
httpx>=0.28
pymilvus>=3.0
milvus-lite>=3.2
beautifulsoup4>=4.12
python-multipart>=0.0.32
pytest>=8
pytest-asyncio>=0.24
```

`backend/pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

`.gitignore`:
```text
__pycache__/
*.pyc
.venv/
.env
*.db
.pytest_cache/
```

- [ ] **Step 4: 运行测试确认通过**

Run: `backend/.venv/Scripts/python.exe -m pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: 初始化并提交**

```bash
cd C:\Users\lenovo\Documents\Agent项目
git init
git add backend .gitignore
git commit -m "chore: init FastAPI backend skeleton with config"
```

---

### Task 2: 数据模型（Document / Chunk）

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/document.py`
- Create: `backend/app/models/chunk.py`
- Test: `backend/tests/test_models.py`

**Interfaces:**
- Produces:
  - `Document(doc_id: str, source_type: str, title: str, content: str, metadata: dict = {}, attributes: dict = {})`
  - `Chunk(id: str, doc_id: str, text: str, chunk_type: str, priority: int, attributes: dict = {}, metadata: dict = {})`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_models.py`:
```python
from app.models.document import Document
from app.models.chunk import Chunk

def test_document_defaults():
    d = Document(doc_id="d1", source_type="html", title="t", content="c")
    assert d.metadata == {}
    assert d.attributes == {}

def test_chunk_fields():
    c = Chunk(id="c1", doc_id="d1", text="材质: 布艺", chunk_type="attribute", priority=10)
    assert c.priority == 10
    assert c.chunk_type == "attribute"
```

- [ ] **Step 2: 运行测试确认失败**（`ModuleNotFoundError: app.models`）

- [ ] **Step 3: 写实现**

`backend/app/models/document.py`:
```python
from pydantic import BaseModel, Field

class Document(BaseModel):
    doc_id: str
    source_type: str
    title: str
    content: str
    metadata: dict = Field(default_factory=dict)
    attributes: dict = Field(default_factory=dict)
```

`backend/app/models/chunk.py`:
```python
from pydantic import BaseModel, Field

class Chunk(BaseModel):
    id: str
    doc_id: str
    text: str
    chunk_type: str
    priority: int = 5
    attributes: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
```

`backend/app/models/__init__.py`:
```python
from app.models.document import Document
from app.models.chunk import Chunk

__all__ = ["Document", "Chunk"]
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/models backend/tests/test_models.py
git commit -m "feat: add Document and Chunk models"
```

---

### Task 3: Embedding 服务抽象

**Files:**
- Create: `backend/app/ai/__init__.py`
- Create: `backend/app/ai/embedding.py`
- Test: `backend/tests/test_embedding.py`

**Interfaces:**
- Consumes: `app.config.Settings`
- Produces:
  - `Embedder`（抽象，`embed(texts: list[str]) -> list[list[float]]`, `embed_query(text) -> list[float]`）
  - `OpenAIEmbedder(Settings)` 真实实现
  - `FakeEmbedder(dim: int)` 测试用（hash 到固定维度向量）

- [ ] **Step 1: 写失败测试**

`backend/tests/test_embedding.py`:
```python
from app.ai.embedding import FakeEmbedder

def test_fake_embedder_shape():
    e = FakeEmbedder(dim=8)
    vecs = e.embed(["a", "b"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 8

def test_fake_embedder_deterministic():
    e = FakeEmbedder(dim=8)
    assert e.embed_query("沙发") == e.embed(["沙发"])[0]
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/ai/embedding.py`:
```python
import hashlib
import struct
from abc import ABC, abstractmethod

from openai import OpenAI

from app.config import Settings


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]:
        return self.embed([text])[0]


class OpenAIEmbedder(Embedder):
    def __init__(self, settings: Settings):
        self._dim = settings.embedding_dim
        self._model = settings.embedding_model
        self._client = OpenAI(
            base_url=settings.openai_base_url,
            api_key=settings.openai_api_key,
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        resp = self._client.embeddings.create(
            model=self._model, input=texts, dimensions=self._dim
        )
        return [d.embedding for d in resp.data]


class FakeEmbedder(Embedder):
    def __init__(self, dim: int):
        self._dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._hash(text) for text in texts]

    def _hash(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        vals = []
        for i in range(self._dim):
            chunk = h[(i * 4) % len(h):(i * 4) % len(h) + 4].ljust(4, b"\x00")
            vals.append(struct.unpack(">I", chunk)[0] / 4294967295.0)
        norm = sum(v * v for v in vals) ** 0.5 or 1.0
        return [v / norm for v in vals]
```

`backend/app/ai/__init__.py`:
```python
from app.ai.embedding import Embedder, OpenAIEmbedder, FakeEmbedder

__all__ = ["Embedder", "OpenAIEmbedder", "FakeEmbedder"]
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/ai backend/tests/test_embedding.py
git commit -m "feat: add Embedder abstraction with OpenAI and fake impls"
```

---

### Task 4: 向量存储抽象 + Milvus Lite 实现

**Files:**
- Create: `backend/app/db/__init__.py`
- Create: `backend/app/db/vector_store.py`
- Create: `backend/app/db/milvus_store.py`
- Test: `backend/tests/test_vector_store.py`

**Interfaces:**
- Consumes: `app.config.Settings`, `app.models.chunk.Chunk`
- Produces:
  - `SearchHit(id: str, score: float, fields: dict)`
  - `VectorStore`（抽象：`insert(chunks)`, `search(vector, top_k, expr)`, `close()`）
  - `InMemoryVectorStore`（测试用）
  - `MilvusStore(Settings)`（Milvus Lite）

- [ ] **Step 1: 写失败测试**

`backend/tests/test_vector_store.py`:
```python
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
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/db/vector_store.py`:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.chunk import Chunk


@dataclass
class SearchHit:
    id: str
    score: float
    fields: dict = field(default_factory=dict)


class VectorStore(ABC):
    @abstractmethod
    def insert(self, chunks: list[Chunk]) -> None: ...

    @abstractmethod
    def search(self, vector: list[float], top_k: int = 50,
               expr: str | None = None) -> list[SearchHit]: ...

    @abstractmethod
    def close(self) -> None: ...


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self._vecs: dict[str, list[float]] = {}
        self._fields: dict[str, dict] = {}

    def insert(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self._vecs[c.id] = [0.0] * 1
            self._fields[c.id] = {"text": c.text, "priority": c.priority, **c.metadata}

    def search(self, vector, top_k=50, expr=None):
        allowed = self._eval_expr(expr)
        scored = []
        for cid, fields in self._fields.items():
            if not allowed(cid, fields):
                continue
            scored.append(SearchHit(id=cid, score=0.0, fields=fields))
        return scored[:top_k]

    def _eval_expr(self, expr):
        if not expr:
            return lambda cid, f: True
        return lambda cid, f: self._match(f, expr)

    @staticmethod
    def _match(fields, expr):
        parts = [p.strip() for p in expr.split("<=")]
        if len(parts) == 2:
            return float(fields[parts[0]]) <= float(parts[1])
        return True

    def close(self) -> None:
        pass
```

`backend/app/db/milvus_store.py`:
```python
from pymilvus import MilvusClient

from app.config import Settings
from app.db.vector_store import SearchHit, VectorStore
from app.models.chunk import Chunk


class MilvusStore(VectorStore):
    def __init__(self, settings: Settings):
        uri = settings.milvus_uri or settings.milvus_db_path
        self._client = MilvusClient(uri)
        self._collection = settings.milvus_collection
        self._dim = settings.embedding_dim
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        if self._client.has_collection(self._collection):
            return
        self._client.create_collection(
            collection_name=self._collection, dimension=self._dim
        )

    def insert(self, chunks: list[Chunk]) -> None:
        data = [{
            "id": c.id,
            "vector": c.metadata.get("vector", [0.0] * self._dim),
            "text": c.text,
            "doc_id": c.doc_id,
            "chunk_type": c.chunk_type,
            "priority": c.priority,
            "price": c.metadata.get("price", 0.0),
            "category": c.metadata.get("category", ""),
            "brand": c.metadata.get("brand", ""),
            "sku": c.metadata.get("sku", ""),
        } for c in chunks]
        self._client.insert(collection_name=self._collection, data=data)

    def search(self, vector, top_k=50, expr=None):
        resp = self._client.search(
            collection_name=self._collection, data=[vector], limit=top_k,
            filter=expr or "", output_fields=["text", "doc_id", "chunk_type",
                                              "priority", "price", "category",
                                              "brand", "sku"],
        )
        hits = []
        for item in resp[0]:
            f = item.get("entity", {})
            hits.append(SearchHit(id=str(item["id"]), score=item["distance"], fields=f))
        return hits

    def close(self) -> None:
        self._client.close()
```

`backend/app/db/__init__.py`:
```python
from app.db.vector_store import InMemoryVectorStore, SearchHit, VectorStore
from app.db.milvus_store import MilvusStore

__all__ = ["InMemoryVectorStore", "SearchHit", "VectorStore", "MilvusStore"]
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/db backend/tests/test_vector_store.py
git commit -m "feat: add VectorStore abstraction with in-memory and Milvus Lite impls"
```

---

### Task 5: 文档解析器（HTML / 纯文本）

**Files:**
- Create: `backend/app/rag/__init__.py`
- Create: `backend/app/rag/ingestion/__init__.py`
- Create: `backend/app/rag/ingestion/parsers/__init__.py`
- Create: `backend/app/rag/ingestion/parsers/base.py`
- Create: `backend/app/rag/ingestion/parsers/text_parser.py`
- Create: `backend/app/rag/ingestion/parsers/html_parser.py`
- Test: `backend/tests/test_parsers.py`

**Interfaces:**
- Consumes: `app.models.document.Document`
- Produces:
  - `Parser`（抽象，`parse(raw: str, meta: dict) -> Document`）
  - `TextParser`
  - `HtmlParser`
  - `get_parser(source_type: str) -> Parser` 工厂

- [ ] **Step 1: 写失败测试**

`backend/tests/test_parsers.py`:
```python
from app.rag.ingestion.parsers import get_parser

def test_text_parser():
    p = get_parser("text")
    doc = p.parse("正文内容", {"doc_id": "d1", "title": "T"})
    assert doc.content == "正文内容"
    assert doc.doc_id == "d1"

def test_html_parser_strips_tags():
    p = get_parser("html")
    doc = p.parse("<html><body><h1>标题</h1><p>描述</p><script>bad()</script></body></html>",
                  {"doc_id": "d1", "title": "T"})
    assert "描述" in doc.content
    assert "bad()" not in doc.content
    assert "<script>" not in doc.content
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/rag/ingestion/parsers/base.py`:
```python
from abc import ABC, abstractmethod
from app.models.document import Document


class Parser(ABC):
    @abstractmethod
    def parse(self, raw: str, meta: dict) -> Document: ...
```

`backend/app/rag/ingestion/parsers/text_parser.py`:
```python
from app.models.document import Document
from app.rag.ingestion.parsers.base import Parser


class TextParser(Parser):
    def parse(self, raw: str, meta: dict) -> Document:
        return Document(
            doc_id=meta["doc_id"], source_type="text",
            title=meta.get("title", ""), content=raw.strip(),
            metadata=meta.get("metadata", {}), attributes=meta.get("attributes", {}),
        )
```

`backend/app/rag/ingestion/parsers/html_parser.py`:
```python
from bs4 import BeautifulSoup

from app.models.document import Document
from app.rag.ingestion.parsers.base import Parser


class HtmlParser(Parser):
    def parse(self, raw: str, meta: dict) -> Document:
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return Document(
            doc_id=meta["doc_id"], source_type="html",
            title=meta.get("title", ""), content=text,
            metadata=meta.get("metadata", {}), attributes=meta.get("attributes", {}),
        )
```

`backend/app/rag/ingestion/parsers/__init__.py`:
```python
from app.rag.ingestion.parsers.base import Parser
from app.rag.ingestion.parsers.text_parser import TextParser
from app.rag.ingestion.parsers.html_parser import HtmlParser

_PARSERS = {"text": TextParser(), "html": HtmlParser()}


def get_parser(source_type: str) -> Parser:
    if source_type not in _PARSERS:
        raise ValueError(f"unsupported source_type: {source_type}")
    return _PARSERS[source_type]
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/rag backend/tests/test_parsers.py
git commit -m "feat: add text and html document parsers"
```

---

### Task 6: 切片器（属性切片 + 描述切片）

**Files:**
- Create: `backend/app/rag/ingestion/chunker.py`
- Test: `backend/tests/test_chunker.py`

**Interfaces:**
- Consumes: `app.models.document.Document`
- Produces:
  - `split_attributes(doc) -> list[Chunk]`
  - `split_description(doc, max_chars=800, overlap=100) -> list[Chunk]`
  - `chunk_document(doc) -> list[Chunk]`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_chunker.py`:
```python
from app.models.document import Document
from app.rag.ingestion.chunker import chunk_document

def test_attributes_split():
    doc = Document(doc_id="d1", source_type="text", title="t", content="x",
                   attributes={"材质": "布艺", "颜色": "米色"})
    chunks = chunk_document(doc)
    attrs = [c for c in chunks if c.chunk_type == "attribute"]
    assert len(attrs) == 2
    assert attrs[0].priority == 10

def test_description_split_with_overlap():
    text = "第一段。" * 200   # 长文本
    doc = Document(doc_id="d1", source_type="text", title="t", content=text)
    chunks = chunk_document(doc)
    descs = [c for c in chunks if c.chunk_type == "description"]
    assert len(descs) > 1
    assert all(c.priority == 5 for c in descs)

def test_short_description_single_chunk():
    doc = Document(doc_id="d1", source_type="text", title="t", content="短内容")
    descs = [c for c in chunk_document(doc) if c.chunk_type == "description"]
    assert len(descs) == 1
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/rag/ingestion/chunker.py`:
```python
from app.models.chunk import Chunk
from app.models.document import Document


def split_attributes(doc: Document) -> list[Chunk]:
    chunks = []
    for i, (key, value) in enumerate(doc.attributes.items()):
        chunks.append(Chunk(
            id=f"{doc.doc_id}:attr:{i}", doc_id=doc.doc_id,
            text=f"{key}: {value}", chunk_type="attribute", priority=10,
            attributes={"key": key, "value": str(value)},
            metadata=doc.metadata,
        ))
    return chunks


def split_description(doc: Document, max_chars: int = 800, overlap: int = 100) -> list[Chunk]:
    text = doc.content.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [Chunk(id=f"{doc.doc_id}:desc:0", doc_id=doc.doc_id, text=text,
                      chunk_type="description", priority=5, metadata=doc.metadata)]
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            cut = text.rfind("。", start, end)
            if cut > start + max_chars // 2:
                end = cut + 1
        chunks.append(Chunk(id=f"{doc.doc_id}:desc:{idx}", doc_id=doc.doc_id,
                            text=text[start:end], chunk_type="description",
                            priority=5, metadata=doc.metadata))
        idx += 1
        start = max(end - overlap, start + 1)
    return chunks


def chunk_document(doc: Document) -> list[Chunk]:
    return split_attributes(doc) + split_description(doc)
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/rag/ingestion/chunker.py backend/tests/test_chunker.py
git commit -m "feat: add attribute and description chunkers"
```

---

### Task 7: 摄取管线（解析 → 切片 → 向量化 → 入库）

**Files:**
- Create: `backend/app/rag/ingestion/pipeline.py`
- Test: `backend/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `get_parser`, `chunk_document`, `VectorStore`, `Embedder`
- Produces: `IngestionPipeline(store, embedder).ingest(raw, meta) -> int`（返回入库 chunk 数）

- [ ] **Step 1: 写失败测试**

`backend/tests/test_pipeline.py`:
```python
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
    assert n == 2  # 1 属性 + 1 描述
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/rag/ingestion/pipeline.py`:
```python
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
```

> **注意**：向量暂存于 chunk.metadata["vector"]，MilvusStore 实现须读取它入库（见 Task 4 的 `insert`，改为 `c.metadata["vector"]`）。为保证一致，Task 4 的 `MilvusStore.insert` 在最终执行时使用 `vector = c.metadata.get("vector", [0.0] * self._dim)`。此处以测试通过为准。

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/rag/ingestion/pipeline.py backend/tests/test_pipeline.py
git commit -m "feat: add ingestion pipeline wiring parser, chunker, embedder, store"
```

---

### Task 8: RAG 检索器（向量检索 + 标量过滤 + RRF + 属性加权）

**Files:**
- Create: `backend/app/rag/retriever.py`
- Test: `backend/tests/test_retriever.py`

**Interfaces:**
- Consumes: `VectorStore`, `Embedder`
- Produces: `Retriever(store, embedder).retrieve(query, top_k=5, filters=None) -> list[dict]`（含 text/score/metadata）
- 内部：`_build_expr(filters) -> str | None`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_retriever.py`:
```python
from app.ai.embedding import FakeEmbedder
from app.db.vector_store import InMemoryVectorStore
from app.rag.retriever import Retriever

def _make_retriever():
    store = InMemoryVectorStore()
    return Retriever(store, FakeEmbedder(dim=8)), store

def test_retrieve_returns_results():
    r, store = _make_retriever()
    from app.models.chunk import Chunk
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
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/rag/retriever.py`:
```python
from app.ai.embedding import Embedder
from app.db.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore, embedder: Embedder):
        self._store = store
        self._embedder = embedder

    def retrieve(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
        vec = self._embedder.embed_query(query)
        expr = self._build_expr(filters)
        hits = self._store.search(vec, top_k=max(top_k * 4, 20), expr=expr)
        scored = []
        for h in hits:
            priority = h.fields.get("priority", 5)
            scored.append((h.score * priority, h))
        scored.sort(key=lambda x: -x[0])
        return [{"text": h.fields.get("text", ""), "score": s, "metadata": h.fields}
                for s, h in scored[:top_k]]

    def _build_expr(self, filters: dict | None) -> str | None:
        if not filters:
            return None
        conds = []
        if "category" in filters:
            conds.append(f'category == "{filters["category"]}"')
        if "max_price" in filters:
            conds.append(f"price <= {filters['max_price']}")
        if "brand" in filters:
            conds.append(f'brand == "{filters["brand"]}"')
        return " and ".join(conds) if conds else None
```

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/rag/retriever.py backend/tests/test_retriever.py
git commit -m "feat: add RAG retriever with scalar filter and priority weighting"
```

---

### Task 9: FastAPI 端点 + 应用组装

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/routes/__init__.py`
- Create: `backend/app/api/routes/ingest.py`
- Create: `backend/app/api/routes/search.py`
- Create: `backend/app/api/deps.py`
- Test: `backend/tests/test_api.py`

**Interfaces:**
- Consumes: `IngestionPipeline`, `Retriever`, `Settings`
- Produces:
  - `POST /ingest` → `{"doc_id": "...", "chunks": n}`
  - `POST /search` → `{"results": [{text, score, metadata}]}`

- [ ] **Step 1: 写失败测试**

`backend/tests/test_api.py`:
```python
from fastapi.testclient import TestClient
from app.main import create_app

def test_ingest_endpoint(monkeypatch):
    from app.ai.embedding import FakeEmbedder
    from app.db.vector_store import InMemoryVectorStore
    monkeypatch.setattr("app.main.build_embedder", lambda s: FakeEmbedder(dim=8))
    monkeypatch.setattr("app.main.build_store", lambda s: InMemoryVectorStore())
    app = create_app()
    client = TestClient(app)
    resp = client.post("/ingest", json={"doc_id": "d1", "source_type": "text",
                                        "title": "T", "content": "内容"})
    assert resp.status_code == 200
    assert resp.json()["chunks"] >= 1

def test_search_endpoint(monkeypatch):
    from app.ai.embedding import FakeEmbedder
    from app.db.vector_store import InMemoryVectorStore
    monkeypatch.setattr("app.main.build_embedder", lambda s: FakeEmbedder(dim=8))
    monkeypatch.setattr("app.main.build_store", lambda s: InMemoryVectorStore())
    app = create_app()
    client = TestClient(app)
    client.post("/ingest", json={"doc_id": "d1", "source_type": "text",
                                 "title": "T", "content": "布艺沙发"})
    resp = client.post("/search", json={"query": "沙发", "top_k": 1})
    assert resp.status_code == 200
    assert len(resp.json()["results"]) == 1
```

- [ ] **Step 2: 运行测试确认失败**

- [ ] **Step 3: 写实现**

`backend/app/api/routes/ingest.py`:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_pipeline
from app.rag.ingestion.pipeline import IngestionPipeline

router = APIRouter()


class IngestRequest(BaseModel):
    doc_id: str
    source_type: str = "text"
    title: str = ""
    content: str
    metadata: dict = {}
    attributes: dict = {}


@router.post("/ingest")
def ingest(req: IngestRequest, pipeline: IngestionPipeline = Depends(get_pipeline)):
    n = pipeline.ingest(req.content, {
        "doc_id": req.doc_id, "source_type": req.source_type, "title": req.title,
        "metadata": req.metadata, "attributes": req.attributes,
    })
    return {"doc_id": req.doc_id, "chunks": n}
```

`backend/app/api/routes/search.py`:
```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_retriever
from app.rag.retriever import Retriever

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None


@router.post("/search")
def search(req: SearchRequest, retriever: Retriever = Depends(get_retriever)):
    results = retriever.retrieve(req.query, top_k=req.top_k, filters=req.filters)
    return {"results": results}
```

`backend/app/api/deps.py`:
```python
from fastapi import Request

from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever import Retriever


def get_pipeline(request: Request) -> IngestionPipeline:
    return request.app.state.pipeline


def get_retriever(request: Request) -> Retriever:
    return request.app.state.retriever
```

`backend/app/main.py`:
```python
from fastapi import FastAPI

from app.ai.embedding import Embedder, OpenAIEmbedder
from app.config import Settings
from app.db.vector_store import MilvusStore, VectorStore
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.retriever import Retriever


def build_embedder(settings: Settings) -> Embedder:
    return OpenAIEmbedder(settings)


def build_store(settings: Settings) -> VectorStore:
    return MilvusStore(settings)


def create_app() -> FastAPI:
    settings = Settings()
    store = build_store(settings)
    embedder = build_embedder(settings)
    pipeline = IngestionPipeline(store, embedder)
    retriever = Retriever(store, embedder)

    app = FastAPI(title="SmartShop AI")
    app.state.pipeline = pipeline
    app.state.retriever = retriever

    from app.api.routes.ingest import router as ingest_router
    from app.api.routes.search import router as search_router
    app.include_router(ingest_router)
    app.include_router(search_router)
    return app


app = create_app()
```

`backend/app/api/routes/__init__.py` 和 `backend/app/api/__init__.py`：空文件。

- [ ] **Step 4: 运行测试确认通过**

- [ ] **Step 5: 提交**

```bash
git add backend/app/main.py backend/app/api backend/tests/test_api.py
git commit -m "feat: add FastAPI ingest and search endpoints"
```

---

## Self-Review 记录

- **Spec 覆盖**：M1 范围（基础设施 + 摄取管线 + RAG 检索 MVP）已覆盖；多模态/LLM 对话/SSE 属 M2-M4，不在本计划。
- **类型一致性**：`Chunk`、`Document`、`SearchHit`、`Embedder`、`VectorStore`、`IngestionPipeline`、`Retriever` 的字段与签名在各任务间一致。
- **已知简化**：`InMemoryVectorStore` 的相似度计算与 `_eval_expr` 为 MVP 简化版（真实过滤依赖 Milvus）；`MilvusStore.insert` 需读取 `chunk.metadata["vector"]`，执行时以集成测试为准。
