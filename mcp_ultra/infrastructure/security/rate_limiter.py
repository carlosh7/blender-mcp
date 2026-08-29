"""
blender-mcp-ultra — Rate Limiter
Implements rate limiting to prevent abuse and DoS attacks.
Uses token bucket algorithm for smooth rate limiting.
"""

import threading
import time
from dataclasses import dataclass


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    pass


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # Max burst requests
    cooldown_seconds: int = 60  # Cooldown after exceeded


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""

    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float  # tokens per second

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens.

        Returns:
            True if tokens consumed, False if rate limited
        """
        now = time.time()

        # Refill tokens
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait until tokens available."""
        if self.tokens >= tokens:
            return 0.0
        return (tokens - self.tokens) / self.refill_rate


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.

    Features:
    - Per-user rate limiting
    - Configurable limits
    - Cooldown after exceeded
    - Thread-safe
    """

    def __init__(self, config: RateLimitConfig | None = None):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self.buckets: dict[str, TokenBucket] = {}
        self.cooldowns: dict[str, float] = {}
        self.lock = threading.Lock()

        # Statistics
        self.total_requests = 0
        self.total_limited = 0

    def _get_or_create_bucket(self, key: str) -> TokenBucket:
        """Get or create token bucket for key."""
        if key not in self.buckets:
            refill_rate = self.config.requests_per_minute / 60.0
            self.buckets[key] = TokenBucket(
                capacity=self.config.burst_size,
                tokens=self.config.burst_size,
                last_refill=time.time(),
                refill_rate=refill_rate,
            )
        return self.buckets[key]

    def check(self, key: str, tokens: int = 1) -> bool:
        """
        Check if request is allowed.

        Args:
            key: Identifier (e.g., user ID, IP address)
            tokens: Number of tokens to consume

        Returns:
            True if allowed, False if rate limited
        """
        with self.lock:
            self.total_requests += 1

            # Check cooldown
            if key in self.cooldowns:
                if time.time() < self.cooldowns[key]:
                    self.total_limited += 1
                    return False
                else:
                    del self.cooldowns[key]

            # Check rate limit
            bucket = self._get_or_create_bucket(key)
            if bucket.consume(tokens):
                return True

            # Rate limited
            self.total_limited += 1

            # Set cooldown if exceeded repeatedly
            if self.total_limited > self.config.requests_per_minute:
                self.cooldowns[key] = time.time() + self.config.cooldown_seconds

            return False

    def wait(self, key: str, tokens: int = 1) -> None:
        """
        Wait until request is allowed.

        Args:
            key: Identifier
            tokens: Number of tokens to consume

        Raises:
            RateLimitExceeded: If wait time too long
        """
        with self.lock:
            bucket = self._get_or_create_bucket(key)
            wait_time = bucket.get_wait_time(tokens)

            if wait_time > self.config.cooldown_seconds:
                raise RateLimitExceeded(
                    f"Rate limit exceeded for {key}. Wait {wait_time:.1f}s or try again later."
                )

        # Wait outside lock
        if wait_time > 0:
            time.sleep(wait_time)

    def reset(self, key: str | None = None) -> None:
        """
        Reset rate limit state.

        Args:
            key: Specific key to reset, or None for all
        """
        with self.lock:
            if key:
                self.buckets.pop(key, None)
                self.cooldowns.pop(key, None)
            else:
                self.buckets.clear()
                self.cooldowns.clear()

    def get_stats(self) -> dict[str, any]:
        """Get rate limiter statistics."""
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "total_limited": self.total_limited,
                "limit_rate": (
                    self.total_limited / self.total_requests * 100 if self.total_requests > 0 else 0
                ),
                "active_buckets": len(self.buckets),
                "active_cooldowns": len(self.cooldowns),
            }

    def set_config(self, config: RateLimitConfig) -> None:
        """Update rate limit configuration."""
        self.config = config
        # Reset all buckets with new config
        self.reset()


# Singleton instance
_limiter = None


def get_limiter(**kwargs) -> RateLimiter:
    """Get singleton rate limiter instance."""
    global _limiter
    if _limiter is None:
        _limiter = RateLimiter(**kwargs)
    return _limiter


def check_rate_limit(key: str, tokens: int = 1) -> bool:
    """Convenience function to check rate limit."""
    return get_limiter().check(key, tokens)
