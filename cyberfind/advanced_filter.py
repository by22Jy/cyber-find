"""
Advanced Filtering Module - Фильтрация результатов по разным критериям
"""

from enum import Enum
from typing import Callable, List

from .models import SearchResult


class PriorityLevel(Enum):
    """Приоритеты платформ"""

    CRITICAL = 10
    HIGH = 9
    MEDIUM = 7
    LOW = 5
    VERY_LOW = 3


class ConfidenceLevel(Enum):
    """Уровни доверия к результатам"""

    VERY_HIGH = 0.95
    HIGH = 0.80
    MEDIUM = 0.60
    LOW = 0.40


class ResultFilter:
    """Продвинутая фильтрация результатов поиска"""

    @staticmethod
    def filter_by_found(results: List[SearchResult]) -> List[SearchResult]:
        """Оставить только найденные аккаунты"""
        return [r for r in results if r.found]

    @staticmethod
    def filter_by_site_category(
        results: List[SearchResult],
        categories: List[str],
    ) -> List[SearchResult]:
        """Фильтр по категориям сайтов (social_media, programming, gaming и т.д.)"""
        return [r for r in results if r.category in categories]

    @staticmethod
    def filter_by_priority(
        results: List[SearchResult],
        min_priority: int = 5,
    ) -> List[SearchResult]:
        """Фильтр по минимальному приоритету платформы"""
        return [r for r in results if r.priority >= min_priority]

    @staticmethod
    def filter_by_confidence(
        results: List[SearchResult],
        min_confidence: float = 0.60,
    ) -> List[SearchResult]:
        """Фильтр по минимальному уровню доверия"""
        return [r for r in results if r.confidence >= min_confidence]

    @staticmethod
    def filter_by_status_code(
        results: List[SearchResult],
        status_codes: List[int],
    ) -> List[SearchResult]:
        """Фильтр по HTTP статус кодам"""
        return [r for r in results if r.status_code in status_codes]

    @staticmethod
    def sort_by_priority(results: List[SearchResult]) -> List[SearchResult]:
        """Сортировка по приоритету платформы (убывание)"""
        return sorted(results, key=lambda r: r.priority, reverse=True)

    @staticmethod
    def sort_by_confidence(results: List[SearchResult]) -> List[SearchResult]:
        """Сортировка по уровню доверия (убывание)"""
        return sorted(results, key=lambda r: r.confidence, reverse=True)

    @staticmethod
    def sort_by_site_name(results: List[SearchResult]) -> List[SearchResult]:
        """Сортировка по названию сайта (А-Я)"""
        return sorted(results, key=lambda r: r.site)

    @staticmethod
    def group_by_category(
        results: List[SearchResult],
    ) -> dict:
        """Группировка результатов по категориям"""
        grouped = {}
        for result in results:
            category = result.category or "other"
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)
        return grouped

    @staticmethod
    def get_top_n(results: List[SearchResult], n: int = 10) -> List[SearchResult]:
        """Получить топ N результатов по приоритету и доверию"""
        sorted_results = sorted(
            results,
            key=lambda r: (r.priority, r.confidence),
            reverse=True,
        )
        return sorted_results[:n]

    @staticmethod
    def apply_custom_filter(
        results: List[SearchResult],
        filter_func: Callable[[SearchResult], bool],
    ) -> List[SearchResult]:
        """Применить кастомный фильтр (функция)"""
        return [r for r in results if filter_func(r)]

    @staticmethod
    def get_statistics(results: List[SearchResult]) -> dict:
        """Получить статистику по результатам"""
        found = [r for r in results if r.found]
        not_found = [r for r in results if not r.found]

        return {
            "total": len(results),
            "found": len(found),
            "not_found": len(not_found),
            "success_rate": len(found) / len(results) if results else 0,
            "avg_confidence": sum(r.confidence for r in found) / len(found) if found else 0,
            "by_category": ResultFilter.group_by_category(results),
            "high_priority_found": len([r for r in found if r.priority >= 8]),
            "very_high_confidence": len([r for r in found if r.confidence >= 0.95]),
        }
