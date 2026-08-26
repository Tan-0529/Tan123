from app.models.document import Document
from app.rag.ingestion.parsers.base import Parser


class TextParser(Parser):
    def parse(self, raw: str, meta: dict) -> Document:
        return Document(
            doc_id=meta["doc_id"], source_type="text",
            title=meta.get("title", ""), content=raw.strip(),
            metadata=meta.get("metadata", {}), attributes=meta.get("attributes", {}),
        )
