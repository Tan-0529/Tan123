import uuid
from collections.abc import AsyncIterator

from app.ai.llm import LLM
from app.ai.prompt import build_messages
from app.core.memory import MemoryStore
from app.rag.retriever import Retriever


def _format_context(results: list[dict]) -> str:
    lines = []
    for i, r in enumerate(results):
        lines.append(f"[{i + 1}] {r['text']}")
    return "\n".join(lines)


def _extract_cards(results: list[dict]) -> list[dict]:
    cards = []
    seen = set()
    for r in results:
        meta = r.get("metadata", {})
        sku = meta.get("sku") or meta.get("doc_id") or ""
        if not sku or sku in seen:
            continue
        seen.add(sku)
        cards.append({
            "name": meta.get("title") or meta.get("doc_id") or "",
            "price": meta.get("price", 0.0),
            "rating": meta.get("rating", 0.0),
            "image_url": meta.get("image_url", ""),
            "product_url": meta.get("product_url", ""),
            "sku": sku,
        })
    return cards


class Orchestrator:
    def __init__(self, retriever: Retriever, llm: LLM, memory: MemoryStore):
        self._retriever = retriever
        self._llm = llm
        self._memory = memory

    async def stream_chat(self, conversation_id: str, message: str) -> AsyncIterator[dict]:
        message_id = uuid.uuid4().hex
        yield {"event": "meta", "conversation_id": conversation_id, "message_id": message_id}

        history = self._memory.get_history(conversation_id)
        results = self._retriever.retrieve(message, top_k=5)
        context = _format_context(results)
        messages = build_messages(history, context, message)

        self._memory.add_turn(conversation_id, "user", message)

        for card in _extract_cards(results):
            yield {"event": "card", "data": card}

        full = ""
        try:
            async for token in self._llm.stream_chat(messages):
                full += token
                yield {"event": "delta", "content": token}
        except Exception as exc:
            yield {"event": "error", "message": str(exc)}
            return

        self._memory.add_turn(conversation_id, "assistant", full)
        yield {"event": "done"}
