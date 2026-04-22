from __future__ import annotations

from src.modules.users import User, UserService


def test_identify_reuses_user_record() -> None:
    service = UserService()
    first = service.identify(telegram_user_id=123, username="alice")
    second = service.identify(telegram_user_id=123, username="alice")

    assert first is second
    assert int(first.user_id) == 123
    assert first.username == "alice"


def test_identify_updates_username_when_provided() -> None:
    service = UserService()
    first = service.identify(telegram_user_id=123, username=None)
    second = service.identify(telegram_user_id=123, username="alice")

    assert first is second
    assert second.username == "alice"


def test_identify_calls_on_user_created_once() -> None:
    created: list[int] = []

    def on_created(user: User) -> None:
        created.append(int(user.user_id))

    service = UserService(on_user_created=on_created)
    first, first_created = service.get_or_create(telegram_user_id=1, username="a")
    second, second_created = service.get_or_create(telegram_user_id=1, username="a2")

    assert first is second
    assert first_created is True
    assert second_created is False
    assert created == [1]
