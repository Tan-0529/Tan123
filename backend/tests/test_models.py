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
