"""
Proxy Support Module - Управление прокси-серверами
"""

import random
from typing import Dict, List, Optional

import aiohttp


class ProxyManager:
    """Управляет прокси-серверами для анонимных запросов"""

    def __init__(self):
        self.proxies: List[str] = []
        self.current_index: int = 0
        self.failed_proxies: List[str] = []
        self.proxy_stats: Dict[str, Dict] = {}

    def load_proxies_from_file(self, file_path: str) -> int:
        """
        Загрузить прокси из файла

        Args:
            file_path: Путь к файлу с прокси (по одному на строку)

        Returns:
            Количество загруженных прокси
        """
        try:
            with open(file_path, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
                self.proxies = proxies
                self._init_proxy_stats()
                return len(proxies)
        except FileNotFoundError:
            return 0

    def load_proxies_from_list(self, proxies: List[str]) -> int:
        """
        Загрузить прокси из списка

        Args:
            proxies: Список прокси (http://ip:port или socks5://ip:port)

        Returns:
            Количество загруженных прокси
        """
        self.proxies = [p.strip() for p in proxies if p.strip()]
        self._init_proxy_stats()
        return len(self.proxies)

    def _init_proxy_stats(self) -> None:
        """Инициализировать статистику для каждого прокси"""
        for proxy in self.proxies:
            if proxy not in self.proxy_stats:
                self.proxy_stats[proxy] = {
                    "requests": 0,
                    "success": 0,
                    "failed": 0,
                    "success_rate": 1.0,
                }

    def get_next_proxy(self) -> Optional[str]:
        """
        Получить следующий прокси (round-robin)

        Returns:
            URL прокси или None если нет доступных
        """
        if not self.proxies:
            return None

        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]

        if not available_proxies:
            # Сбросить список неудачных и попробовать снова
            self.failed_proxies.clear()
            available_proxies = self.proxies

        proxy = available_proxies[self.current_index % len(available_proxies)]
        self.current_index += 1
        return proxy

    def get_random_proxy(self) -> Optional[str]:
        """
        Получить случайный прокси из доступных

        Returns:
            URL прокси или None
        """
        if not self.proxies:
            return None

        available_proxies = [p for p in self.proxies if p not in self.failed_proxies]

        if not available_proxies:
            self.failed_proxies.clear()
            available_proxies = self.proxies

        return random.choice(available_proxies)

    def get_best_proxy(self) -> Optional[str]:
        """
        Получить прокси с наибольшей успешностью

        Returns:
            URL лучшего прокси
        """
        if not self.proxies:
            return None

        available = [p for p in self.proxies if p not in self.failed_proxies]
        if not available:
            return random.choice(self.proxies) if self.proxies else None

        return max(available, key=lambda p: self.proxy_stats[p]["success_rate"])

    async def validate_proxy(self, proxy: str, test_url: str = "http://httpbin.org/ip") -> bool:
        """
        Проверить рабочесть прокси

        Args:
            proxy: URL прокси для проверки
            test_url: URL для тестирования

        Returns:
            True если прокси рабочий, False иначе
        """
        try:
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=5)

            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy, timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False

    def report_success(self, proxy: str) -> None:
        """Зафиксировать успешное использование прокси"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats["requests"] += 1
            stats["success"] += 1
            stats["success_rate"] = stats["success"] / stats["requests"]

    def report_failure(self, proxy: str) -> None:
        """Зафиксировать ошибку при использовании прокси"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats["requests"] += 1
            stats["failed"] += 1
            stats["success_rate"] = stats["success"] / stats["requests"]

            # Если неудачный процент слишком высок, добавить в чёрный список
            if stats["success_rate"] < 0.3:
                self.failed_proxies.append(proxy)

    def get_proxy_stats(self) -> Dict:
        """Получить статистику прокси"""
        return self.proxy_stats.copy()

    def clear_failed(self) -> None:
        """Очистить список неудачных прокси"""
        self.failed_proxies.clear()

    def remove_proxy(self, proxy: str) -> None:
        """Удалить прокси из списка"""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
        if proxy in self.failed_proxies:
            self.failed_proxies.remove(proxy)

    def get_proxy_count(self) -> Dict:
        """
        Получить информацию о количестве прокси

        Returns:
            Словарь с информацией о прокси
        """
        return {
            "total": len(self.proxies),
            "available": len(self.proxies) - len(self.failed_proxies),
            "failed": len(self.failed_proxies),
        }
