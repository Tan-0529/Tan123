import pytest

from app.ai.llm import FakeLLM


@pytest.mark.asyncio
async def test_fake_llm_streams_full_response():
    llm = FakeLLM("你好，我是导购", chunk_size=2)
    chunks = [c async for c in llm.stream_chat([])]
    assert "".join(chunks) == "你好，我是导购"
    assert len(chunks) > 1
