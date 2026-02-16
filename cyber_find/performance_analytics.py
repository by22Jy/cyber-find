"""
Performance Analytics Module - Search performance analysis
"""

import asyncio
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class SearchMetrics:
    """Metrics for a single search"""

    username: str
    total_sites: int
    found_count: int
    failed_count: int
    start_time: float
    end_time: float
    duration_seconds: float
    sites_per_second: float
    success_rate: float
    timestamp: str


class PerformanceAnalytics:
    """Analyzes search performance"""

    def __init__(self):
        self.searches: List[SearchMetrics] = []
        self.current_search_start: Optional[float] = None
        self.current_search_data: Optional[Dict] = None
        self._lock = asyncio.Lock()  # Add thread-safe lock for async operations

    def start_search(self, username: str, total_sites: int) -> None:
        """
        Start tracking a search

        Args:
            username: Username
            total_sites: Total number of sites
        """
        self.current_search_start = time.time()
        self.current_search_data = {
            "username": username,
            "total_sites": total_sites,
            "found_count": 0,
            "failed_count": 0,
        }

    def end_search(
        self,
        found_count: int = 0,
        failed_count: int = 0,
    ) -> SearchMetrics:
        """
        End tracking a search

        Args:
            found_count: Number of found profiles
            failed_count: Number of errors

        Returns:
            Search metrics
        """
        if not self.current_search_start or not self.current_search_data:
            raise RuntimeError("No active search")

        end_time = time.time()
        start_time = self.current_search_start
        duration = end_time - start_time

        total_sites = self.current_search_data["total_sites"]
        success_rate = (found_count / total_sites) if total_sites > 0 else 0

        metrics = SearchMetrics(
            username=self.current_search_data["username"],
            total_sites=total_sites,
            found_count=found_count,
            failed_count=failed_count,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            sites_per_second=total_sites / duration if duration > 0 else 0,
            success_rate=success_rate,
            timestamp=datetime.now().isoformat(),
        )

        # Thread-safe append
        self.searches.append(metrics)
        self.current_search_start = None
        self.current_search_data = None

        return metrics

    def get_average_performance(self) -> Dict:
        """
        Get average performance

        Returns:
            Dictionary with average values
        """
        if not self.searches:
            return {}

        total_duration = sum(s.duration_seconds for s in self.searches)
        total_sites = sum(s.total_sites for s in self.searches)
        total_found = sum(s.found_count for s in self.searches)
        total_failed = sum(s.failed_count for s in self.searches)

        return {
            "average_duration": total_duration / len(self.searches),
            "average_sites_per_second": total_sites / total_duration if total_duration > 0 else 0,
            "average_success_rate": total_found / total_sites if total_sites > 0 else 0,
            "total_searches": len(self.searches),
            "total_sites_searched": total_sites,
            "total_found": total_found,
            "total_failed": total_failed,
        }

    def get_bottlenecks(self) -> List[Dict]:
        """
        Find performance bottlenecks

        Returns:
            List of bottlenecks with recommendations
        """
        if not self.searches:
            return []

        bottlenecks = []

        # Slow searches
        avg_duration = sum(s.duration_seconds for s in self.searches) / len(self.searches)
        slow_searches = [s for s in self.searches if s.duration_seconds > avg_duration * 2]

        if slow_searches:
            bottlenecks.append(
                {
                    "type": "slow_search",
                    "count": len(slow_searches),
                    "recommendation": "Consider using parallel requests",
                    "examples": [s.username for s in slow_searches[:3]],
                }
            )

        # High failure rate
        avg_failures = sum(s.failed_count for s in self.searches) / len(self.searches)
        high_failure = [s for s in self.searches if s.failed_count > avg_failures * 2]

        if high_failure:
            bottlenecks.append(
                {
                    "type": "high_failure_rate",
                    "count": len(high_failure),
                    "recommendation": "Add proxies or increase delay between requests",
                    "examples": [s.username for s in high_failure[:3]],
                }
            )

        # Low processing speed
        slow_speed = [s for s in self.searches if s.sites_per_second < 1]
        if slow_speed:
            bottlenecks.append(
                {
                    "type": "slow_processing",
                    "count": len(slow_speed),
                    "recommendation": "Optimize network requests or use caching",
                    "examples": [s.username for s in slow_speed[:3]],
                }
            )

        return bottlenecks

    def get_optimization_suggestions(self) -> List[str]:
        """
        Get optimization recommendations

        Returns:
            List of recommendations
        """
        suggestions: List[str] = []

        if not self.searches:
            return suggestions

        avg_performance = self.get_average_performance()

        # Slow processing
        if avg_performance.get("average_sites_per_second", 0) < 2:
            suggestions.append("Increase request parallelism (batch_size)")

        # Low success rate
        if avg_performance.get("average_success_rate", 0) < 0.5:
            suggestions.append("Use proxies to increase success rate")

        # High failure count
        if avg_performance.get("total_failed", 0) > avg_performance.get("total_found", 0):
            suggestions.append("Enable rate limiting to reduce blocks")

        # Long searches
        if avg_performance.get("average_duration", 0) > 30:
            suggestions.append("Use async operations for parallel processing")

        return suggestions

    def get_detailed_report(self) -> Dict:
        """
        Get detailed performance report

        Returns:
            Detailed report
        """
        return {
            "total_searches": len(self.searches),
            "average_performance": self.get_average_performance(),
            "bottlenecks": self.get_bottlenecks(),
            "suggestions": self.get_optimization_suggestions(),
            "all_metrics": [asdict(s) for s in self.searches[-10:]],  # Последние 10 поисков
        }

    def predict_search_duration(self, num_sites: int) -> float:
        """
        Predict search duration based on history

        Args:
            num_sites: Number of sites to search

        Returns:
            Predicted duration in seconds
        """
        if not self.searches:
            return num_sites * 0.5  # По умолчанию 0.5 сек/сайт

        avg_speed = sum(s.sites_per_second for s in self.searches) / len(self.searches)
        return num_sites / avg_speed if avg_speed > 0 else num_sites * 0.5

    def compare_searches(self, username1: str, username2: str) -> Dict:
        """
        Compare performance of two searches

        Args:
            username1: First username
            username2: Second username

        Returns:
            Comparative analysis
        """
        search1 = next((s for s in self.searches if s.username == username1), None)
        search2 = next((s for s in self.searches if s.username == username2), None)

        if not search1 or not search2:
            return {}

        return {
            "faster_search": (
                username1 if search1.duration_seconds < search2.duration_seconds else username2
            ),
            "duration_difference": abs(search1.duration_seconds - search2.duration_seconds),
            "success_difference": abs(search1.success_rate - search2.success_rate),
            "search1": asdict(search1),
            "search2": asdict(search2),
        }

    def export_metrics_json(self) -> str:
        """
        Export metrics to JSON format

        Returns:
            JSON string with metrics
        """
        import json

        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_average_performance(),
            "searches": [asdict(s) for s in self.searches],
            "bottlenecks": self.get_bottlenecks(),
            "suggestions": self.get_optimization_suggestions(),
        }

        return json.dumps(data, ensure_ascii=False, indent=2)
