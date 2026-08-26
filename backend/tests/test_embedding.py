from app.ai.embedding import FakeEmbedder


def test_fake_embedder_shape():
    e = FakeEmbedder(dim=8)
    vecs = e.embed(["a", "b"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 8


def test_fake_embedder_deterministic():
    e = FakeEmbedder(dim=8)
    assert e.embed_query("沙发") == e.embed(["沙发"])[0]
