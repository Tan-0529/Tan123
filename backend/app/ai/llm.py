from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import Settings


class LLM(ABC):
    @abstractmethod
    def stream_chat(self, messages: list[dict]) -> AsyncIterator[str]: ...


class OpenAILLM(LLM):
    def __init__(self, settings: Settings):
        self._model = settings.llm_model
        self._base_url = settings.openai_base_url
        self._api_key = settings.openai_api_key
        self._client = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(base_url=self._base_url, api_key=self._api_key)
        return self._client

    async def stream_chat(self, messages: list[dict]) -> AsyncIterator[str]:
        stream = await self._get_client().chat.completions.create(
            model=self._model, messages=messages, stream=True, temperature=0.7,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class FakeLLM(LLM):
    def __init__(self, response: str, chunk_size: int = 4):
        self._response = response
        self._chunk_size = chunk_size

    async def stream_chat(self, messages: list[dict]) -> AsyncIterator[str]:
        for i in range(0, len(self._response), self._chunk_size):
            yield self._response[i:i + self._chunk_size]
