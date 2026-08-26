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
    text = "第一段。" * 250
    doc = Document(doc_id="d1", source_type="text", title="t", content=text)
    chunks = chunk_document(doc)
    descs = [c for c in chunks if c.chunk_type == "description"]
    assert len(descs) > 1
    assert all(c.priority == 5 for c in descs)


def test_short_description_single_chunk():
    doc = Document(doc_id="d1", source_type="text", title="t", content="短内容")
    descs = [c for c in chunk_document(doc) if c.chunk_type == "description"]
    assert len(descs) == 1
