"""
Unit tests for reverse_search module
"""

import pytest

from cyber_find.models import SearchResult, SearchStatus
from cyber_find.reverse_search import ReverseSearch


@pytest.mark.unit
class TestReverseSearch:
    """Test ReverseSearch functionality"""

    def test_search_by_partial_match(self):
        """Test searching by partial username match"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/john_doe",
                status=SearchStatus.FOUND,
                username="john_doe",
            ),
            SearchResult(
                site="github",
                url="https://github.com/johndoe",
                status=SearchStatus.FOUND,
                username="johndoe",
            ),
            SearchResult(
                site="facebook",
                url="https://facebook.com/janedoe",
                status=SearchStatus.FOUND,
                username="janedoe",
            ),
        ]

        matches = ReverseSearch.search_by_partial_match("john", results)
        assert len(matches) == 2
        assert all("john" in (m.username or "").lower() for m in matches)

    def test_search_by_partial_match_no_results(self):
        """Test searching with no matches"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/john",
                status=SearchStatus.FOUND,
                username="john",
            ),
        ]

        matches = ReverseSearch.search_by_partial_match("xyz", results)
        assert len(matches) == 0

    def test_search_by_email_domain(self):
        """Test searching by email domain"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                metadata={"email_domain": "gmail.com"},
            ),
            SearchResult(
                site="github",
                url="https://github.com/test",
                status=SearchStatus.FOUND,
                metadata={"email_domain": "outlook.com"},
            ),
        ]

        matches = ReverseSearch.search_by_email_domain("gmail.com", results)
        assert len(matches) == 1
        assert matches[0].site == "twitter"

    def test_search_by_email_domain_no_metadata(self):
        """Test searching when no metadata exists"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/test",
                status=SearchStatus.FOUND,
                metadata={},
            ),
        ]

        matches = ReverseSearch.search_by_email_domain("gmail.com", results)
        assert len(matches) == 0

    def test_find_similar_usernames(self):
        """Test finding similar usernames"""
        usernames = ["john_doe", "john_doe_123", "johndoe", "jane_doe"]

        similar = ReverseSearch.find_similar_usernames("john_doe", usernames)
        assert isinstance(similar, list)
        # Should find at least some similar names
        assert len(similar) > 0

    def test_find_similar_usernames_exact_match(self):
        """Test finding exact match"""
        usernames = ["john_doe", "other_user"]

        similar = ReverseSearch.find_similar_usernames("john_doe", usernames)
        assert "john_doe" in similar

    def test_find_similar_usernames_empty_list(self):
        """Test with empty username list"""
        similar = ReverseSearch.find_similar_usernames("test", [])
        assert similar == []

    def test_find_similar_usernames_high_threshold(self):
        """Test with high similarity threshold"""
        usernames = ["john_doe", "john_doe_123", "completely_different"]

        similar = ReverseSearch.find_similar_usernames("john_doe", usernames, threshold=0.9)
        # With high threshold, only very similar names should match
        assert isinstance(similar, list)

    def test_empty_results(self):
        """Test handling empty results"""
        results = []

        matches = ReverseSearch.search_by_partial_match("test", results)
        assert matches == []

        matches = ReverseSearch.search_by_email_domain("test.com", results)
        assert matches == []

    def test_partial_match_case_insensitive(self):
        """Test that partial match is case insensitive"""
        results = [
            SearchResult(
                site="twitter",
                url="https://twitter.com/JohnDoe",
                status=SearchStatus.FOUND,
                username="JohnDoe",
            ),
        ]

        matches_lower = ReverseSearch.search_by_partial_match("john", results)
        matches_upper = ReverseSearch.search_by_partial_match("JOHN", results)

        assert len(matches_lower) == 1
        assert len(matches_upper) == 1
