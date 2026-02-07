"""
Batch Search Module - Поиск по нескольким юзернеймам одновременно
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from .core import CyberFind
from .models import SearchResult


class BatchSearch:
    """Batch поиск для нескольких юзернеймов с оптимизацией"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)

    async def batch_search(
        self,
        usernames: List[str],
        sites_file: str = "quick.txt",
        mode: str = "standard",
    ) -> Dict[str, List[SearchResult]]:
        """
        Массовый поиск для нескольких юзернеймов

        Args:
            usernames: Список юзернеймов
            sites_file: Файл со списком сайтов
            mode: Режим поиска (standard, deep, stealth, aggressive)

        Returns:
            Dict с результатами поиска для каждого юзернейма
        """
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def search_with_limit(username: str):
            async with semaphore:
                try:
                    found = await cf.search(
                        username=username,
                        sites_file=sites_file,
                        mode=mode,
                    )
                    return username, found
                except Exception:
                    return username, []

        tasks = [search_with_limit(username) for username in usernames]
        search_results = await asyncio.gather(*tasks)

        for username, found in search_results:
            results[username] = found

        return results

    async def batch_search_by_site(
        self,
        usernames: List[str],
        site: str,
    ) -> Dict[str, bool]:
        """Быстрый поиск на одном конкретном сайте для всех юзернеймов"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(username: str):
            async with semaphore:
                try:
                    found = await cf.check_user_exists(username, site)
                    return username, found
                except Exception:
                    return username, False

        tasks = [check_site(username) for username in usernames]
        check_results = await asyncio.gather(*tasks)

        for username, exists in check_results:
            results[username] = exists

        return results

    async def batch_search_multiple_sites(
        self,
        username: str,
        sites: List[str],
    ) -> Dict[str, bool]:
        """Поиск одного юзернейма на нескольких сайтах параллельно"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(site: str):
            async with semaphore:
                try:
                    found = await cf.check_user_exists(username, site)
                    return site, found
                except Exception:
                    return site, False

        tasks = [check_site(site) for site in sites]
        check_results = await asyncio.gather(*tasks)

        for site, exists in check_results:
            results[site] = exists

        return results
