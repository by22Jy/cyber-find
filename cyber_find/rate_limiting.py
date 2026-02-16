"""
Rate Limiting Module - Request rate management
"""

import asyncio
import time
from enum import Enum
from typing import Dict, Optional


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""

    FIXED = "fixed"  # Fixed delay
    LINEAR = "linear"  # Linear increase
    EXPONENTIAL = "exponential"  # Exponential increase


class RateLimiter:
    """Manages request rate to avoid bans"""

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: int = 5,
        strategy: RateLimitStrategy = RateLimitStrategy.FIXED,
    ):
        """
        Initialize rate limiter

        Args:
            requests_per_second: Maximum requests per second
            burst_size: Burst size (max concurrent requests)
            strategy: Rate limiting strategy
        """
        self.requests_per_second = requests_per_second
        self.burst_size = burst_size
        self.strategy = strategy

        self.last_request_time: Dict[str, float] = {}
        self.request_count: Dict[str, int] = {}
        self.failure_count: Dict[str, int] = {}

        # Token bucket для управления скоростью
        self.tokens: float = burst_size
        self.max_tokens: float = burst_size
        self.last_refill: float = time.time()

    async def acquire(self, domain: str = "default") -> None:
        """
        Acquire permission for request

        Args:
            domain: Domain requiring rate limiting
        """
        self._refill_tokens()

        while self.tokens < 1:
            await asyncio.sleep(1 / self.requests_per_second)
            self._refill_tokens()

        self.tokens -= 1
        self.last_request_time[domain] = time.time()
        self.request_count[domain] = self.request_count.get(domain, 0) + 1

    def _refill_tokens(self) -> None:
        """Refill tokens (token bucket algorithm)"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.requests_per_second

        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_wait_time(self, domain: str = "default") -> float:
        """
        Get wait time before next request

        Args:
            domain: Domain

        Returns:
            Wait time in seconds
        """
        if domain not in self.last_request_time:
            return 0.0

        last_time = self.last_request_time[domain]
        min_interval = 1 / self.requests_per_second

        elapsed = time.time() - last_time
        wait_time = max(0, min_interval - elapsed)

        return wait_time

    async def backoff(
        self,
        attempt: int,
        max_retries: int = 5,
        strategy: Optional[RateLimitStrategy] = None,
    ) -> None:
        """
        Exponential backoff for retry attempts

        Args:
            attempt: Attempt number (starting from 1)
            max_retries: Maximum retry attempts
            strategy: Strategy (if None, uses default)
        """
        if attempt > max_retries:
            raise Exception(f"Exceeded max retries ({max_retries})")

        if strategy is None:
            strategy = self.strategy

        if strategy == RateLimitStrategy.FIXED:
            wait_time = 2
        elif strategy == RateLimitStrategy.LINEAR:
            wait_time = 2 * attempt
        elif strategy == RateLimitStrategy.EXPONENTIAL:
            wait_time = 2**attempt
        else:
            wait_time = 2

        # Add small randomness (jitter)
        import random

        jitter = random.uniform(0, 0.1 * wait_time)
        total_wait = min(wait_time + jitter, 300)  # Макс 5 минут

        await asyncio.sleep(total_wait)

    def report_success(self, domain: str = "default") -> None:
        """Record successful request"""
        self.failure_count[domain] = 0

    def report_failure(self, domain: str = "default") -> None:
        """Record error"""
        self.failure_count[domain] = self.failure_count.get(domain, 0) + 1

    def should_backoff(self, domain: str = "default", threshold: int = 3) -> bool:
        """
        Determine if backoff is needed based on error count

        Args:
            domain: Domain
            threshold: Error threshold for backoff

        Returns:
            True if backoff is needed
        """
        return self.failure_count.get(domain, 0) >= threshold

    def get_adaptive_delay(self, domain: str = "default") -> float:
        """
        Get adaptive delay based on error history

        Args:
            domain: Domain

        Returns:
            Recommended delay in seconds
        """
        failures = self.failure_count.get(domain, 0)
        base_delay = 1 / self.requests_per_second

        # Увеличить задержку на 50% за каждую ошибку
        return base_delay * (1.5**failures)

    def reset_domain(self, domain: str) -> None:
        """Reset statistics for domain"""
        self.last_request_time.pop(domain, None)
        self.request_count.pop(domain, None)
        self.failure_count.pop(domain, None)

    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            "requests_per_second": self.requests_per_second,
            "current_tokens": self.tokens,
            "domains": {
                domain: {
                    "requests": self.request_count.get(domain, 0),
                    "failures": self.failure_count.get(domain, 0),
                }
                for domain in set(
                    list(self.request_count.keys()) + list(self.failure_count.keys())
                )
            },
        }

    async def wait_until_ready(self, requests: int = 1, domain: str = "default") -> None:
        """
        Wait until enough tokens are available for N requests

        Args:
            requests: Number of requests
            domain: Domain
        """
        for _ in range(requests):
            await self.acquire(domain)
