from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal, NewType, Protocol, TypedDict

UserId = NewType("UserId", int)
ChatRole = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


class OllamaTagModel(TypedDict):
    name: str


class OllamaTagsResponse(TypedDict):
    models: list[OllamaTagModel]


class OllamaClient(Protocol):
    async def list_models(self) -> list[str]: ...

    async def generate_once(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float | None = None,
        timeout: float | None = None,
        run_id: str | None = None,
        step_index: int | None = None,
        request_kind: str | None = None,
        retry_index: int | None = None,
    ) -> str: ...

    async def generate_streamed_text(
        self,
        prompt: str,
        *,
        model: str,
        timeout: float | None = None,
        on_thinking_chunk: Callable[[str], None] | None = None,
        on_content_chunk: Callable[[str], None] | None = None,
        on_stream_done: Callable[[], None] | None = None,
        run_id: str | None = None,
        step_index: int | None = None,
    ) -> tuple[str, str]: ...

    async def chat_once(self, messages: Sequence["ChatMessage"], *, model: str) -> str: ...


class ToolCall(TypedDict):
    tool: str
    args: dict[str, Any]


@dataclass(slots=True)
class LLMReply:
    llm_raw: str
    bot_reply: str
    thinking: str = ""
