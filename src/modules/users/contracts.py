from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

UserId = NewType("UserId", int)


@dataclass(frozen=True, slots=True)
class UserIdentity:
    user_id: UserId
    username: str | None = None

