from app.rag.ingestion.parsers.base import Parser
from app.rag.ingestion.parsers.text_parser import TextParser
from app.rag.ingestion.parsers.html_parser import HtmlParser

_PARSERS = {"text": TextParser(), "html": HtmlParser()}


def get_parser(source_type: str) -> Parser:
    if source_type not in _PARSERS:
        raise ValueError(f"unsupported source_type: {source_type}")
    return _PARSERS[source_type]
