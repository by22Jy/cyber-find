"""
Advanced Filtering Module - Filter results by various criteria
"""

from enum import Enum
from typing import Callable, Dict, List

from .models import SearchResult


class PriorityLevel(Enum):
    """Platform priorities"""

    CRITICAL = 10
    HIGH = 9
    MEDIUM = 7
    LOW = 5
    VERY_LOW = 3


class ConfidenceLevel(Enum):
    """Confidence levels for results"""

    VERY_HIGH = 0.95
    HIGH = 0.80
    MEDIUM = 0.60
    LOW = 0.40


class ResultFilter:
    """Advanced search result filtering"""

    @staticmethod
    def filter_by_found(results: List[SearchResult]) -> List[SearchResult]:
        """Keep only found accounts"""
        return [r for r in results if r.found]

    @staticmethod
    def filter_by_site_category(
        results: List[SearchResult],
        categories: List[str],
    ) -> List[SearchResult]:
        """Filter by site categories (social_media, programming, gaming, etc.)"""
        return [r for r in results if r.category in categories]

    @staticmethod
    def filter_by_priority(
        results: List[SearchResult],
        min_priority: int = 5,
    ) -> List[SearchResult]:
        """Filter by minimum platform priority"""
        return [r for r in results if r.priority >= min_priority]

    @staticmethod
    def filter_by_confidence(
        results: List[SearchResult],
        min_confidence: float = 0.60,
    ) -> List[SearchResult]:
        """Filter by minimum confidence level"""
        return [r for r in results if r.confidence >= min_confidence]

    @staticmethod
    def filter_by_status_code(
        results: List[SearchResult],
        status_codes: List[int],
    ) -> List[SearchResult]:
        """Filter by HTTP status codes"""
        return [r for r in results if r.status_code in status_codes]

    @staticmethod
    def sort_by_priority(results: List[SearchResult]) -> List[SearchResult]:
        """Sort by platform priority (descending)"""
        return sorted(results, key=lambda r: r.priority, reverse=True)

    @staticmethod
    def sort_by_confidence(results: List[SearchResult]) -> List[SearchResult]:
        """Sort by confidence level (descending)"""
        return sorted(results, key=lambda r: r.confidence, reverse=True)

    @staticmethod
    def sort_by_site_name(results: List[SearchResult]) -> List[SearchResult]:
        """Sort by site name (A-Z)"""
        return sorted(results, key=lambda r: r.site)

    @staticmethod
    def group_by_category(
        results: List[SearchResult],
    ) -> dict:
        """Group results by category"""
        grouped: Dict[str, List[SearchResult]] = {}
        for result in results:
            category = result.category or "other"
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(result)
        return grouped

    @staticmethod
    def get_top_n(results: List[SearchResult], n: int = 10) -> List[SearchResult]:
        """Get top N results by priority and confidence"""
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
        """Apply custom filter (function)"""
        return [r for r in results if filter_func(r)]

    @staticmethod
    def get_statistics(results: List[SearchResult]) -> dict:
        """Get statistics for results"""
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
