from abc import ABC, abstractmethod
from collections import defaultdict, deque


class MemoryStore(ABC):
    @abstractmethod
    def get_history(self, conversation_id: str) -> list[dict]: ...

    @abstractmethod
    def add_turn(self, conversation_id: str, role: str, content: str) -> None: ...


class InMemoryMemory(MemoryStore):
    def __init__(self, max_turns: int = 20):
        self._max_turns = max_turns
        self._data: dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_turns)
        )

    def get_history(self, conversation_id: str) -> list[dict]:
        return list(self._data[conversation_id])

    def add_turn(self, conversation_id: str, role: str, content: str) -> None:
        self._data[conversation_id].append({"role": role, "content": content})
