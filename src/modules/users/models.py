from __future__ import annotations

from dataclasses import dataclass

from .contracts import UserId


@dataclass(slots=True)
class User:
    user_id: UserId
    username: str | None = None

