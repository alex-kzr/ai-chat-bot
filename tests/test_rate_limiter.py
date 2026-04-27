import asyncio

import pytest

from src.services.rate_limiter import RateLimiter, TokenBucket


class TestTokenBucket:
    """Token bucket unit tests."""

    def test_initial_tokens_equal_capacity(self) -> None:
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        assert bucket.tokens == 5

    def test_consume_succeeds_when_tokens_available(self) -> None:
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        assert bucket.try_consume(1) is True
        assert bucket.tokens == 4

    def test_consume_fails_when_insufficient_tokens(self) -> None:
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        bucket.tokens = 0
        assert bucket.try_consume(1) is False

    def test_tokens_do_not_exceed_capacity(self) -> None:
        import time

        bucket = TokenBucket(capacity=5, refill_rate=10.0)
        bucket.tokens = 3
        time.sleep(0.1)
        bucket.try_consume(0)
        assert bucket.tokens <= 5


class TestRateLimiter:
    """Rate limiter integration tests."""

    @pytest.mark.asyncio
    async def test_single_user_under_limit(self) -> None:
        limiter = RateLimiter(requests_per_minute=20, burst=5)
        user_id = 123
        for _ in range(5):
            assert await limiter.is_allowed(user_id) is True

    @pytest.mark.asyncio
    async def test_single_user_exceeds_burst(self) -> None:
        limiter = RateLimiter(requests_per_minute=20, burst=5)
        user_id = 123
        for _ in range(5):
            assert await limiter.is_allowed(user_id) is True
        assert await limiter.is_allowed(user_id) is False

    @pytest.mark.asyncio
    async def test_different_users_have_separate_limits(self) -> None:
        limiter = RateLimiter(requests_per_minute=20, burst=5)
        user1, user2 = 123, 456
        for _ in range(5):
            assert await limiter.is_allowed(user1) is True
        for _ in range(5):
            assert await limiter.is_allowed(user2) is True
        assert await limiter.is_allowed(user1) is False
        assert await limiter.is_allowed(user2) is False

    @pytest.mark.asyncio
    async def test_user_can_make_new_request_after_refill(self) -> None:

        limiter = RateLimiter(requests_per_minute=60, burst=2)
        user_id = 123
        assert await limiter.is_allowed(user_id) is True
        assert await limiter.is_allowed(user_id) is True
        assert await limiter.is_allowed(user_id) is False
        await asyncio.sleep(1.1)
        assert await limiter.is_allowed(user_id) is True
