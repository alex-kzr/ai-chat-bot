from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class ChatMessage(TypedDict):
    role: str
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
