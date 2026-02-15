"""
Unit tests for rate_limiting module
"""

import asyncio

import pytest

from cyber_find.rate_limiting import RateLimiter, RateLimitStrategy


@pytest.mark.unit
class TestRateLimiter:
    """Test RateLimiter functionality"""

    def test_initialization(self):
        """Test RateLimiter initialization"""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=5)

        assert limiter.requests_per_second == 2.0
        assert limiter.burst_size == 5
        assert limiter.max_tokens == 5
        assert limiter.tokens == 5

    def test_token_initialization(self):
        """Test token initialization"""
        limiter = RateLimiter(requests_per_second=1.0, burst_size=10)

        assert limiter.tokens == 10
        assert limiter.max_tokens == 10

    @pytest.mark.asyncio
    async def test_acquire(self):
        """Test token acquisition"""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=5)

        # Should succeed as we have tokens
        await limiter.acquire()
        assert limiter.tokens < 5

    @pytest.mark.asyncio
    async def test_acquire_domain(self):
        """Test token acquisition for specific domain"""
        limiter = RateLimiter(requests_per_second=10.0, burst_size=5)

        await limiter.acquire("github.com")
        assert "github.com" in limiter.last_request_time

    def test_get_wait_time(self):
        """Test wait time calculation"""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=5)

        # No requests made yet
        wait_time = limiter.get_wait_time()
        assert wait_time == 0.0

    def test_report_success(self):
        """Test success reporting"""
        limiter = RateLimiter()

        limiter.report_success("github.com")
        assert limiter.failure_count.get("github.com", 0) == 0

    def test_report_failure(self):
        """Test failure reporting"""
        limiter = RateLimiter()

        limiter.report_failure("github.com")
        assert limiter.failure_count.get("github.com", 0) == 1

    def test_should_backoff(self):
        """Test backoff decision"""
        limiter = RateLimiter()

        # No backoff at first
        assert not limiter.should_backoff("github.com")

        # Add some failures
        for _ in range(3):
            limiter.report_failure("github.com")

        assert limiter.should_backoff("github.com")

    def test_get_stats(self):
        """Test statistics retrieval"""
        limiter = RateLimiter(requests_per_second=2.0, burst_size=5)

        stats = limiter.get_stats()
        assert stats["requests_per_second"] == 2.0
        assert stats["current_tokens"] == 5

    def test_reset_domain(self):
        """Test domain reset"""
        limiter = RateLimiter()

        limiter.report_failure("github.com")
        assert limiter.failure_count.get("github.com", 0) > 0

        limiter.reset_domain("github.com")
        assert limiter.failure_count.get("github.com", 0) == 0


@pytest.mark.unit
class TestBackoffStrategies:
    """Test different backoff strategies"""

    @pytest.mark.asyncio
    async def test_fixed_backoff(self):
        """Test FIXED backoff strategy"""
        limiter = RateLimiter(strategy=RateLimitStrategy.FIXED)

        import time

        start = time.time()
        await limiter.backoff(1, max_retries=5, strategy=RateLimitStrategy.FIXED)
        elapsed = time.time() - start

        # Fixed backoff is 2 seconds
        assert elapsed >= 1.9

    @pytest.mark.asyncio
    async def test_linear_backoff(self):
        """Test LINEAR backoff strategy"""
        limiter = RateLimiter(strategy=RateLimitStrategy.LINEAR)

        import time

        start = time.time()
        await limiter.backoff(1, max_retries=5, strategy=RateLimitStrategy.LINEAR)
        elapsed = time.time() - start

        # Linear: 2 * 1 = 2 seconds
        assert elapsed >= 1.9

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test EXPONENTIAL backoff strategy"""
        limiter = RateLimiter(strategy=RateLimitStrategy.EXPONENTIAL)

        import time

        start = time.time()
        await limiter.backoff(1, max_retries=5, strategy=RateLimitStrategy.EXPONENTIAL)
        elapsed = time.time() - start

        # Exponential: 2^1 = 2 seconds
        assert elapsed >= 1.9

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test max retries exceeded"""
        limiter = RateLimiter()

        with pytest.raises(Exception):
            await limiter.backoff(10, max_retries=5)

    def test_adaptive_delay(self):
        """Test adaptive delay calculation"""
        limiter = RateLimiter(requests_per_second=2.0)

        limiter.report_failure("github.com")
        delay = limiter.get_adaptive_delay("github.com")

        assert delay > 0
