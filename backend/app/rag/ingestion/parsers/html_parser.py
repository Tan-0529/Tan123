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
