from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, NewType, TypedDict

UserId = NewType("UserId", int)
ChatRole = Literal["system", "user", "assistant"]


class ChatMessage(TypedDict):
    role: ChatRole
    content: str


class OllamaTagModel(TypedDict):
    name: str


class OllamaTagsResponse(TypedDict):
    models: list[OllamaTagModel]


class ToolCall(TypedDict):
    tool: str
    args: dict[str, Any]


@dataclass(slots=True)
class LLMReply:
    llm_raw: str
    bot_reply: str
    thinking: str = ""
