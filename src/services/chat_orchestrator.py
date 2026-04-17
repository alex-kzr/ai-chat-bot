from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from src.contracts import LLMReply
from src.llm import ask_llm
from src.conversation import ConversationService
from src.agent.service import AgentOrchestrator

logger = logging.getLogger(__name__)
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


@dataclass(slots=True)
class ChatOutcome:
    reply: str
    llm_raw: str
    used_agent: bool


@dataclass(slots=True)
class ChatOrchestrator:
    conversation: ConversationService
    agent: AgentOrchestrator
    show_thinking: bool

    async def process_text(self, user_id: int, text: str) -> ChatOutcome:
        if _URL_RE.search(text):
            answer = await self.agent.run_task(text)
            return ChatOutcome(reply=answer, llm_raw=answer, used_agent=True)

        await self.conversation.maybe_compress_history(user_id)
        self.conversation.append_message(user_id, "user", text)
        history = self.conversation.get_history(user_id)

        reply: LLMReply = await ask_llm(text, history=history, user_id=user_id)
        user_reply = reply.bot_reply
        if self.show_thinking and reply.thinking:
            user_reply = f"💭 <thinking>\n{reply.thinking}\n</thinking>\n\n{reply.bot_reply}"

        if reply.llm_raw != "[error]":
            self.conversation.append_message(user_id, "assistant", user_reply)
        return ChatOutcome(reply=user_reply, llm_raw=reply.llm_raw, used_agent=False)
