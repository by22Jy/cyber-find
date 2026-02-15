"""
Rate Limiting Module - Управление частотой запросов
"""

import asyncio
import time
from enum import Enum
from typing import Dict, Optional


class RateLimitStrategy(Enum):
    """Стратегии ограничения частоты"""

    FIXED = "fixed"  # Фиксированная задержка
    LINEAR = "linear"  # Линейное увеличение
    EXPONENTIAL = "exponential"  # Экспоненциальное увеличение


class RateLimiter:
    """Управляет частотой запросов для избежания бана"""

    def __init__(
        self,
        requests_per_second: float = 1.0,
        burst_size: int = 5,
        strategy: RateLimitStrategy = RateLimitStrategy.FIXED,
    ):
        """
        Инициализировать rate limiter

        Args:
            requests_per_second: Максимум запросов в секунду
            burst_size: Размер всплеска (макс одновременных запросов)
            strategy: Стратегия ограничения
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
        Получить разрешение на запрос

        Args:
            domain: Домен для которого нужно ограничение
        """
        self._refill_tokens()

        while self.tokens < 1:
            await asyncio.sleep(1 / self.requests_per_second)
            self._refill_tokens()

        self.tokens -= 1
        self.last_request_time[domain] = time.time()
        self.request_count[domain] = self.request_count.get(domain, 0) + 1

    def _refill_tokens(self) -> None:
        """Пополнить токены (token bucket алгоритм)"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.requests_per_second

        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def get_wait_time(self, domain: str = "default") -> float:
        """
        Получить время ожидания перед следующим запросом

        Args:
            domain: Домен

        Returns:
            Время ожидания в секундах
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
        Экспоненциальная задержка для повторных попыток

        Args:
            attempt: Номер попытки (начиная с 1)
            max_retries: Максимум повторных попыток
            strategy: Стратегия (если None, используется стандартная)
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

        # Добавить небольшую случайность (jitter)
        import random

        jitter = random.uniform(0, 0.1 * wait_time)
        total_wait = min(wait_time + jitter, 300)  # Макс 5 минут

        await asyncio.sleep(total_wait)

    def report_success(self, domain: str = "default") -> None:
        """Зафиксировать успешный запрос"""
        self.failure_count[domain] = 0

    def report_failure(self, domain: str = "default") -> None:
        """Зафиксировать ошибку"""
        self.failure_count[domain] = self.failure_count.get(domain, 0) + 1

    def should_backoff(self, domain: str = "default", threshold: int = 3) -> bool:
        """
        Нужно ли делать backoff на основе количества ошибок

        Args:
            domain: Домен
            threshold: Порог ошибок для backoff

        Returns:
            True если нужен backoff
        """
        return self.failure_count.get(domain, 0) >= threshold

    def get_adaptive_delay(self, domain: str = "default") -> float:
        """
        Получить адаптивную задержку на основе истории ошибок

        Args:
            domain: Домен

        Returns:
            Рекомендуемая задержка в секундах
        """
        failures = self.failure_count.get(domain, 0)
        base_delay = 1 / self.requests_per_second

        # Увеличить задержку на 50% за каждую ошибку
        return base_delay * (1.5**failures)

    def reset_domain(self, domain: str) -> None:
        """Сбросить статистику для домена"""
        self.last_request_time.pop(domain, None)
        self.request_count.pop(domain, None)
        self.failure_count.pop(domain, None)

    def get_stats(self) -> Dict:
        """Получить статистику"""
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
        Ждать пока будет достаточно токенов для N запросов

        Args:
            requests: Количество запросов
            domain: Домен
        """
        for _ in range(requests):
            await self.acquire(domain)
