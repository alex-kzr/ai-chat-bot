from __future__ import annotations

from .contracts import ChatMessage, LLMReply
from .modules.chat.service import ChatService


async def ask_llm(
    user_text: str,
    history: list[ChatMessage] | None = None,
    user_id: str | int | None = None,
) -> LLMReply:
    """
    Backwards-compatible wrapper over the Chat/AI module boundary.

    Existing tests and call sites import `ask_llm` from `src.llm`. New code should
    prefer using `src.modules.chat.ChatService` via runtime wiring.
    """

    from .runtime import get_runtime

    runtime = get_runtime()
    chat_service: ChatService
    if hasattr(runtime, "chat_service"):
        chat_service = runtime.chat_service
    else:
        chat_service = ChatService(settings=runtime.settings, ollama=runtime.ollama)
    return await chat_service.generate_response(user_text, history=history, user_id=user_id)
