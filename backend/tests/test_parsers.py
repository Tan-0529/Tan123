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
