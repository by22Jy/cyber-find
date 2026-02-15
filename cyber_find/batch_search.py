"""
Batch Search Module - Поиск по нескольким юзернеймам одновременно
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from .core import CyberFind, SearchMode
from .models import SearchResult

logger = logging.getLogger("cyberfind")


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
        from .core import SearchMode

        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def search_with_limit(username: str):
            async with semaphore:
                try:
                    search_mode = SearchMode(mode)
                    found = await cf.search_async(
                        usernames=[username],
                        builtin_list=sites_file.replace(".txt", ""),
                        mode=search_mode,
                    )
                    return username, found.get("results", {}).get(username, {})
                except Exception as e:
                    logger.error(f"Batch search error for {username}: {e}")
                    return username, {}

        tasks = [search_with_limit(username) for username in usernames]
        search_results = await asyncio.gather(*tasks)

        for username, found in search_results:
            results[username] = found

        return results

    async def batch_search_by_site(
        self,
        usernames: List[str],
        site_name: str,
    ) -> Dict[str, bool]:
        """Быстрый поиск на одном конкретном сайте для всех юзернеймов"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(username: str):
            async with semaphore:
                try:
                    # Load sites and find the specific one
                    sites = await cf.load_sites_async(builtin_list="all")
                    matching_site = next((s for s in sites if s.get("name") == site_name), None)

                    if matching_site:
                        result = await cf.check_site_async(
                            username, matching_site, SearchMode.STANDARD, asyncio.Semaphore(1)
                        )
                        return username, result.get("found", False)
                    return username, False
                except Exception as e:
                    logger.error(f"Error checking {site_name} for {username}: {e}")
                    return username, False

        tasks = [check_site(username) for username in usernames]
        check_results = await asyncio.gather(*tasks)

        for username, exists in check_results:
            results[username] = exists

        return results

    async def batch_search_multiple_sites(
        self,
        username: str,
        site_names: List[str],
    ) -> Dict[str, bool]:
        """Поиск одного юзернейма на нескольких сайтах параллельно"""
        results = {}
        cf = CyberFind()

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def check_site(site_name: str):
            async with semaphore:
                try:
                    # Load sites and find the specific one
                    sites = await cf.load_sites_async(builtin_list="all")
                    matching_site = next((s for s in sites if s.get("name") == site_name), None)

                    if matching_site:
                        result = await cf.check_site_async(
                            username, matching_site, SearchMode.STANDARD, asyncio.Semaphore(1)
                        )
                        return site_name, result.get("found", False)
                    return site_name, False
                except Exception as e:
                    logger.error(f"Error checking {site_name}: {e}")
                    return site_name, False

        tasks = [check_site(site) for site in site_names]
        check_results = await asyncio.gather(*tasks)

        for site, exists in check_results:
            results[site] = exists

        return results
