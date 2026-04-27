import asyncio
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TokenBucket:
    """Token bucket for a single user."""

    capacity: int
    refill_rate: float
    tokens: float = field(default_factory=float)
    last_refill: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)
        self.last_refill = time.time()

    def try_consume(self, amount: int = 1) -> bool:
        """Try to consume tokens, refilling first if needed."""
        now = time.time()
        elapsed = now - self.last_refill
        refill = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + refill)
        self.last_refill = now

        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False


class RateLimiter:
    """Per-user rate limiter using token buckets."""

    def __init__(self, requests_per_minute: int, burst: int) -> None:
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.refill_rate = requests_per_minute / 60.0
        self.buckets: dict[int, TokenBucket] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, user_id: int) -> bool:
        """Check if a user is allowed to make a request."""
        async with self._lock:
            if user_id not in self.buckets:
                self.buckets[user_id] = TokenBucket(
                    capacity=self.burst,
                    refill_rate=self.refill_rate,
                )

            bucket = self.buckets[user_id]
            allowed = bucket.try_consume(1)
            if not allowed:
                logger.info(
                    "rate_limit_exceeded user_id=%s capacity=%s refill_rate=%.2f tokens=%.2f",
                    user_id,
                    self.burst,
                    self.refill_rate,
                    bucket.tokens,
                )
            return allowed
