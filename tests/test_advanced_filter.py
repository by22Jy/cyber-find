"""
Unit tests for advanced_filter module
"""

import pytest

from cyber_find.advanced_filter import ConfidenceLevel, PriorityLevel, ResultFilter
from cyber_find.models import SearchResult, SearchStatus


@pytest.mark.unit
class TestPriorityLevel:
    """Test PriorityLevel enum"""

    def test_priority_levels(self):
        """Test priority level values"""
        assert PriorityLevel.CRITICAL.value == 10
        assert PriorityLevel.HIGH.value == 9
        assert PriorityLevel.MEDIUM.value == 7
        assert PriorityLevel.LOW.value == 5
        assert PriorityLevel.VERY_LOW.value == 3


@pytest.mark.unit
class TestConfidenceLevel:
    """Test ConfidenceLevel enum"""

    def test_confidence_levels(self):
        """Test confidence level values"""
        assert ConfidenceLevel.VERY_HIGH.value == 0.95
        assert ConfidenceLevel.HIGH.value == 0.80
        assert ConfidenceLevel.MEDIUM.value == 0.60
        assert ConfidenceLevel.LOW.value == 0.40


@pytest.mark.unit
class TestResultFilter:
    """Test ResultFilter class"""

    def test_filter_by_found(self):
        """Test filtering by found status"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                confidence=90,
            ),
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.NOT_FOUND,
                confidence=0,
            ),
        ]

        filtered = ResultFilter.filter_by_found(results)
        assert len(filtered) == 1
        assert filtered[0].site == "twitter"

    def test_filter_by_site_category(self):
        """Test filtering by site category"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                category="social_media",
            ),
            SearchResult(
                site="github",
                url="https://github.com/test",
                status=SearchStatus.FOUND,
                category="programming",
            ),
        ]

        filtered = ResultFilter.filter_by_site_category(results, ["social_media"])
        assert len(filtered) == 1
        assert filtered[0].site == "twitter"

    def test_filter_by_priority(self):
        """Test filtering by priority level"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                priority=9,
            ),
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.FOUND,
                priority=3,
            ),
        ]

        filtered = ResultFilter.filter_by_priority(results, min_priority=5)
        assert len(filtered) == 1
        assert filtered[0].site == "twitter"

    def test_filter_by_confidence(self):
        """Test filtering by confidence level"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                confidence=0.90,
            ),
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.FOUND,
                confidence=0.30,
            ),
        ]

        filtered = ResultFilter.filter_by_confidence(results, min_confidence=0.60)
        assert len(filtered) == 1
        assert filtered[0].site == "twitter"

    def test_filter_by_status_code(self):
        """Test filtering by status code"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                status_code=200,
            ),
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.FOUND,
                status_code=404,
            ),
        ]

        filtered = ResultFilter.filter_by_status_code(results, [200])
        assert len(filtered) == 1
        assert filtered[0].site == "twitter"

    def test_sort_by_priority(self):
        """Test sorting by priority"""
        results = [
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.FOUND,
                priority=3,
            ),
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                priority=9,
            ),
        ]

        sorted_results = ResultFilter.sort_by_priority(results)
        assert sorted_results[0].site == "twitter"  # Higher priority first
        assert sorted_results[1].site == "facebook"

    def test_sort_by_confidence(self):
        """Test sorting by confidence"""
        results = [
            SearchResult(
                site="facebook",
                url="https://facebook.com/test",
                status=SearchStatus.FOUND,
                confidence=0.50,
            ),
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                confidence=0.90,
            ),
        ]

        sorted_results = ResultFilter.sort_by_confidence(results)
        assert sorted_results[0].site == "twitter"  # Higher confidence first
        assert sorted_results[1].site == "facebook"

    def test_filter_empty_results(self):
        """Test filtering empty results"""
        results = []
        filtered = ResultFilter.filter_by_found(results)
        assert filtered == []

    def test_sort_empty_results(self):
        """Test sorting empty results"""
        results = []
        sorted_results = ResultFilter.sort_by_confidence(results)
        assert sorted_results == []
