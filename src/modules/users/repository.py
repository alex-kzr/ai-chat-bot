from __future__ import annotations

from .contracts import UserId
from .models import User


class _InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UserId, User] = {}

    def get(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    def add(self, user: User) -> None:
        self._users[user.user_id] = user

