from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias


@dataclass(frozen=True, slots=True)
class UserCreated:
    kind: Literal["user_created"] = "user_created"
    user_id: int = 0
    username: str | None = None


@dataclass(frozen=True, slots=True)
class MessageReceived:
    kind: Literal["message_received"] = "message_received"
    user_id: int = 0
    text: str = ""


@dataclass(frozen=True, slots=True)
class ResponseGenerated:
    kind: Literal["response_generated"] = "response_generated"
    user_id: int = 0
    reply: str = ""
    used_agent: bool = False


@dataclass(frozen=True, slots=True)
class UserTextReceived:
    kind: Literal["user_text_received"] = "user_text_received"
    user_id: int = 0
    text: str = ""


@dataclass(frozen=True, slots=True)
class ChatReplyProduced:
    kind: Literal["chat_reply_produced"] = "chat_reply_produced"
    user_id: int = 0
    reply: str = ""
    used_agent: bool = False


@dataclass(frozen=True, slots=True)
class AgentTaskStarted:
    kind: Literal["agent_task_started"] = "agent_task_started"
    user_id: int = 0
    task: str = ""


@dataclass(frozen=True, slots=True)
class AgentTaskFinished:
    kind: Literal["agent_task_finished"] = "agent_task_finished"
    user_id: int = 0
    task: str = ""
    final_answer: str = ""


AppEvent: TypeAlias = (
    UserCreated
    | MessageReceived
    | ResponseGenerated
    | UserTextReceived
    | ChatReplyProduced
    | AgentTaskStarted
    | AgentTaskFinished
)

ChatEvent: TypeAlias = AppEvent
