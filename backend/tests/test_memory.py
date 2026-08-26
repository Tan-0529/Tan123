from app.core.memory import InMemoryMemory


def test_memory_add_and_get():
    m = InMemoryMemory()
    m.add_turn("c1", "user", "你好")
    m.add_turn("c1", "assistant", "你好，想买什么？")
    h = m.get_history("c1")
    assert len(h) == 2
    assert h[0]["role"] == "user"


def test_memory_isolated_by_conversation():
    m = InMemoryMemory()
    m.add_turn("c1", "user", "a")
    m.add_turn("c2", "user", "b")
    assert len(m.get_history("c1")) == 1
    assert len(m.get_history("c2")) == 1
