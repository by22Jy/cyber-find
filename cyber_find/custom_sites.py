"""
Custom Site Lists Module - Поддержка пользовательских списков сайтов
"""

import os
from typing import Dict, List, Optional


class CustomSiteListManager:
    """Управляет пользовательскими списками сайтов"""

    def __init__(self, default_sites_dir: str = "sites"):
        """
        Инициализировать менеджер

        Args:
            default_sites_dir: Директория со встроенными списками сайтов
        """
        self.default_sites_dir = default_sites_dir
        self.custom_lists: Dict[str, List[Dict]] = {}
        self.default_lists: Dict[str, List[Dict]] = {}

    def load_site_list(self, file_path: str) -> List[Dict]:
        """
        Загрузить список сайтов из файла

        Args:
            file_path: Путь к файлу

        Returns:
            Список сайтов в формате [{"name": "", "url": "", "category": "", "priority": ""}]
        """
        sites: List[Dict[str, str]] = []

        if not os.path.exists(file_path):
            return sites

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split("|")
                    if len(parts) >= 4:
                        site = {
                            "name": parts[0].strip(),
                            "url": parts[1].strip(),
                            "category": parts[2].strip(),
                            "priority": parts[3].strip(),
                        }
                        sites.append(site)
        except Exception:
            pass

        return sites

    def load_custom_list(self, list_name: str, file_path: str) -> int:
        """
        Загрузить пользовательский список сайтов

        Args:
            list_name: Имя списка
            file_path: Путь к файлу

        Returns:
            Количество загруженных сайтов
        """
        sites = self.load_site_list(file_path)
        self.custom_lists[list_name] = sites
        return len(sites)

    def create_custom_list(
        self,
        list_name: str,
        sites: List[Dict],
        output_file: Optional[str] = None,
    ) -> int:
        """
        Создать новый пользовательский список

        Args:
            list_name: Имя списка
            sites: Список сайтов
            output_file: Опционально сохранить в файл

        Returns:
            Количество сайтов в списке
        """
        self.custom_lists[list_name] = sites

        if output_file:
            self.save_list_to_file(output_file, sites)

        return len(sites)

    def save_list_to_file(self, file_path: str, sites: List[Dict]) -> None:
        """
        Сохранить список сайтов в файл

        Args:
            file_path: Путь к файлу
            sites: Список сайтов
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            for site in sites:
                line = f"{site['name']}|{site['url']}|{site.get('category', 'custom')}|{site.get('priority', '5')}\n"
                f.write(line)

    def merge_lists(
        self,
        list_names: List[str],
        remove_duplicates: bool = True,
    ) -> List[Dict]:
        """
        Объединить несколько списков

        Args:
            list_names: Имена списков для объединения
            remove_duplicates: Удалить дубликаты по URL

        Returns:
            Объединённый список
        """
        merged = []
        seen_urls = set()

        for list_name in list_names:
            sites = self.custom_lists.get(list_name, [])
            for site in sites:
                url = site.get("url", "")

                if remove_duplicates:
                    if url not in seen_urls:
                        merged.append(site)
                        seen_urls.add(url)
                else:
                    merged.append(site)

        return merged

    def filter_by_category(
        self,
        list_name: str,
        category: str,
    ) -> List[Dict]:
        """
        Отфильтровать сайты по категории

        Args:
            list_name: Имя списка
            category: Категория

        Returns:
            Отфильтрованный список
        """
        sites = self.custom_lists.get(list_name, [])
        return [s for s in sites if s.get("category") == category]

    def filter_by_priority(
        self,
        list_name: str,
        min_priority: int = 1,
        max_priority: int = 10,
    ) -> List[Dict]:
        """
        Отфильтровать сайты по приоритету

        Args:
            list_name: Имя списка
            min_priority: Минимальный приоритет
            max_priority: Максимальный приоритет

        Returns:
            Отфильтрованный список
        """
        sites = self.custom_lists.get(list_name, [])

        def get_priority(site: Dict) -> int:
            try:
                return int(site.get("priority", 5))
            except ValueError:
                return 5

        return [s for s in sites if min_priority <= get_priority(s) <= max_priority]

    def add_site_to_list(
        self,
        list_name: str,
        site: Dict,
    ) -> None:
        """
        Добавить сайт в список

        Args:
            list_name: Имя списка
            site: Информация о сайте
        """
        if list_name not in self.custom_lists:
            self.custom_lists[list_name] = []

        self.custom_lists[list_name].append(site)

    def remove_site_from_list(
        self,
        list_name: str,
        site_url: str,
    ) -> bool:
        """
        Удалить сайт из списка

        Args:
            list_name: Имя списка
            site_url: URL сайта

        Returns:
            True если сайт найден и удалён
        """
        if list_name not in self.custom_lists:
            return False

        sites = self.custom_lists[list_name]
        for i, site in enumerate(sites):
            if site.get("url") == site_url:
                sites.pop(i)
                return True

        return False

    def get_list_info(self, list_name: str) -> Dict:
        """
        Получить информацию о списке

        Args:
            list_name: Имя списка

        Returns:
            Информация о списке
        """
        sites = self.custom_lists.get(list_name, [])

        categories: Dict[str, int] = {}
        for site in sites:
            cat = site.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "name": list_name,
            "total_sites": len(sites),
            "categories": categories,
            "sites": sites,
        }

    def list_all_lists(self) -> List[str]:
        """
        Получить имена всех загруженных списков

        Returns:
            Список имён
        """
        return list(self.custom_lists.keys())

    def export_list_stats(self) -> Dict:
        """
        Экспортировать статистику всех списков

        Returns:
            Статистика по каждому списку
        """
        stats = {}

        for list_name, sites in self.custom_lists.items():
            categories: Dict[str, int] = {}
            for site in sites:
                cat = site.get("category", "unknown")
                categories[cat] = categories.get(cat, 0) + 1

            stats[list_name] = {
                "total_sites": len(sites),
                "categories": categories,
            }

        return stats
