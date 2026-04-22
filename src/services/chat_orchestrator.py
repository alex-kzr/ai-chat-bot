from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from src.contracts import LLMReply
from src.conversation import ConversationService
from src.agent.service import AgentOrchestrator
from src.events import MessageReceived, ResponseGenerated
from src.events.bus import EventBus
from src.modules.chat.service import ChatService

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
    chat: ChatService
    event_bus: EventBus
    show_thinking: bool

    async def process_text(self, user_id: int, text: str) -> ChatOutcome:
        if _URL_RE.search(text):
            answer = await self.agent.run_task(text)
            return ChatOutcome(reply=answer, llm_raw=answer, used_agent=True)

        await self.conversation.maybe_compress_history(user_id)
        await self.event_bus.publish(MessageReceived(user_id=user_id, text=text))
        history = self.conversation.get_history(user_id)

        reply: LLMReply = await self.chat.generate_response(text, history=history, user_id=user_id)
        user_reply = self.chat.format_for_user(reply, show_thinking=self.show_thinking)

        if reply.llm_raw != "[error]":
            await self.event_bus.publish(ResponseGenerated(user_id=user_id, reply=user_reply, used_agent=False))
        return ChatOutcome(reply=user_reply, llm_raw=reply.llm_raw, used_agent=False)
