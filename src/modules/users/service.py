from __future__ import annotations

from collections.abc import Callable

from .contracts import UserId
from .models import User
from .repository import _InMemoryUserRepository


class UserService:
    def __init__(self, *, on_user_created: Callable[[User], None] | None = None) -> None:
        self._repo = _InMemoryUserRepository()
        self._on_user_created = on_user_created

    def identify(self, telegram_user_id: int, username: str | None) -> User:
        user, _created = self.get_or_create(telegram_user_id=telegram_user_id, username=username)
        return user

    def get_or_create(self, *, telegram_user_id: int, username: str | None) -> tuple[User, bool]:
        user_id = UserId(telegram_user_id)
        existing = self._repo.get(user_id)
        if existing is not None:
            if username and username != existing.username:
                existing.username = username
            return existing, False

        user = User(user_id=user_id, username=username)
        self._repo.add(user)
        if self._on_user_created is not None:
            self._on_user_created(user)
        return user, True
