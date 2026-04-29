"""Test doubles for external I/O boundaries (Ollama and Telegram)."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock

from src.contracts import ChatMessage, LLMReply


# ---------------------------------------------------------------------------
# Ollama gateway fake
# ---------------------------------------------------------------------------

@dataclass
class GatewayCall:
    """Record of a single call made to FakeOllamaGateway."""
    method: str
    model: str
    prompt: str | None = None
    messages: list[dict[str, Any]] | None = None
    options: dict[str, Any] = field(default_factory=dict)


class FakeOllamaGateway:
    """Deterministic Ollama gateway that returns scripted replies without any network I/O.

    Usage::
        gateway = FakeOllamaGateway(script=[
            LLMReply(llm_raw="hi", bot_reply="hi"),
            ValueError("simulated failure"),
        ])
        # first call → LLMReply
        # second call → raises ValueError
    """

    def __init__(self, script: list[LLMReply | BaseException] | None = None) -> None:
        self.script: list[LLMReply | BaseException] = list(script or [])
        self.calls: list[GatewayCall] = []

    def _pop(self) -> LLMReply:
        """Pop next scripted item; raise if it is an exception."""
        if not self.script:
            raise AssertionError("FakeOllamaGateway: script exhausted — no more replies queued")
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    async def generate_once(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float | None = None,
    ) -> str:
        """Return bot_reply from the next scripted LLMReply."""
        self.calls.append(GatewayCall(method="generate_once", model=model, prompt=prompt))
        reply = self._pop()
        return reply.bot_reply

    async def generate_streamed_text(
        self,
        prompt: str,
        *,
        model: str,
        on_thinking_chunk: Callable[[str], None] | None = None,
        on_content_chunk: Callable[[str], None] | None = None,
        on_stream_done: Callable[[], None] | None = None,
    ) -> tuple[str, str]:
        """Return (bot_reply, thinking) from the next scripted LLMReply, firing callbacks."""
        self.calls.append(GatewayCall(method="generate_streamed_text", model=model, prompt=prompt))
        reply = self._pop()
        if on_thinking_chunk and reply.thinking:
            on_thinking_chunk(reply.thinking)
        if on_content_chunk and reply.bot_reply:
            on_content_chunk(reply.bot_reply)
        if on_stream_done:
            on_stream_done()
        return reply.bot_reply, reply.thinking

    async def chat_once(self, messages: Sequence[ChatMessage], *, model: str) -> str:
        """Return bot_reply from the next scripted LLMReply."""
        self.calls.append(
            GatewayCall(
                method="chat_once",
                model=model,
                messages=[dict(m) for m in messages],
            )
        )
        reply = self._pop()
        return reply.bot_reply

    async def list_models(self) -> list[str]:
        """Always returns an empty model list; not scripted."""
        return []


# ---------------------------------------------------------------------------
# Telegram message builders
# ---------------------------------------------------------------------------

def make_message(
    text: str = "hi",
    user_id: int = 42,
    username: str = "alice",
    chat_id: int = 42,
) -> Any:
    """Build an aiogram-compatible Message mock for use in handler tests.

    All awaited methods (answer, bot.send_chat_action) are AsyncMocks.
    """
    from unittest.mock import MagicMock

    msg = MagicMock()
    msg.text = text
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.from_user.username = username
    msg.chat = MagicMock()
    msg.chat.id = chat_id
    msg.bot = MagicMock()
    msg.bot.send_chat_action = AsyncMock()
    msg.answer = AsyncMock()
    return msg


def make_message_with_failing_answer(
    exc: BaseException | None = None,
    text: str = "hi",
    user_id: int = 42,
    username: str = "alice",
    chat_id: int = 42,
) -> Any:
    """Same as make_message but answer() raises exc (default: RuntimeError)."""
    msg = make_message(text=text, user_id=user_id, username=username, chat_id=chat_id)
    msg.answer.side_effect = exc or RuntimeError("Telegram answer failed")
    return msg


