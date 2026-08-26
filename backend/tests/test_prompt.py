from app.ai.prompt import SYSTEM_PROMPT, build_messages


def test_build_messages_order():
    msgs = build_messages(
        history=[{"role": "user", "content": "你好"}, {"role": "assistant", "content": "你好"}],
        context="【检索上下文】\n商品A", query="有沙发吗",
    )
    assert msgs[0]["role"] == "system"
    assert msgs[-1]["role"] == "user"
    assert msgs[-1]["content"] == "有沙发吗"
    assert any("检索上下文" in m["content"] for m in msgs)


def test_system_prompt_mentions_guide():
    assert "导购" in SYSTEM_PROMPT
