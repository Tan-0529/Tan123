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
