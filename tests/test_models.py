"""
Unit tests for models module
"""

from datetime import datetime

import pytest

from cyber_find.models import SearchReport, SearchResult, SearchStatus, UserSearchResults


@pytest.mark.unit
class TestSearchStatus:
    """Test SearchStatus enum"""

    def test_search_status_values(self):
        """Test that SearchStatus has correct values"""
        assert SearchStatus.FOUND.value == "found"
        assert SearchStatus.NOT_FOUND.value == "not_found"
        assert SearchStatus.ERROR.value == "error"
        assert SearchStatus.PENDING.value == "pending"


@pytest.mark.unit
class TestSearchResult:
    """Test SearchResult dataclass"""

    def test_search_result_creation(self):
        """Test creating SearchResult"""
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
        )
        assert result.site == "twitter"
        assert result.url == "https://twitter.com/testuser"
        assert result.status == SearchStatus.FOUND

    def test_search_result_to_dict(self):
        """Test SearchResult to_dict method"""
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
            confidence=90,
        )
        data = result.to_dict()
        assert data["site"] == "twitter"
        assert data["status"] == "found"
        assert data["confidence"] == 90

    def test_search_result_is_success(self):
        """Test is_success property"""
        found = SearchResult(
            site="twitter",
            url="https://twitter.com/test",
            status=SearchStatus.FOUND,
        )
        not_found = SearchResult(
            site="facebook",
            url="https://facebook.com/test",
            status=SearchStatus.NOT_FOUND,
        )
        assert found.is_success is True
        assert not_found.is_success is False

    def test_search_result_found_property(self):
        """Test found property alias"""
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/test",
            status=SearchStatus.FOUND,
        )
        assert result.found is True

    def test_search_result_site_name_property(self):
        """Test site_name property alias"""
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/test",
            status=SearchStatus.FOUND,
        )
        assert result.site_name == "twitter"

    def test_search_result_with_optional_fields(self):
        """Test SearchResult with all optional fields"""
        result = SearchResult(
            site="github",
            url="https://github.com/testuser",
            status=SearchStatus.FOUND,
            status_code=200,
            response_time=0.5,
            error=None,
            metadata={"bio": "Developer"},
            username="testuser",
            confidence=95,
            category="social",
            priority=1,
        )
        assert result.username == "testuser"
        assert result.confidence == 95
        assert result.category == "social"
        assert result.priority == 1


@pytest.mark.unit
class TestUserSearchResults:
    """Test UserSearchResults dataclass"""

    def test_user_search_results_creation(self):
        """Test creating UserSearchResults"""
        user_results = UserSearchResults(username="testuser")
        assert user_results.username == "testuser"
        assert user_results.results == []

    def test_user_search_results_with_results(self):
        """Test UserSearchResults with results"""
        result1 = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
        )
        result2 = SearchResult(
            site="facebook",
            url="https://facebook.com/testuser",
            status=SearchStatus.NOT_FOUND,
        )
        user_results = UserSearchResults(
            username="testuser",
            results=[result1, result2],
            total_sites_checked=2,
        )
        assert len(user_results.results) == 2
        assert user_results.found_count == 1
        assert user_results.not_found_count == 1

    def test_user_search_results_duration(self):
        """Test duration property"""
        start = datetime.now()
        end = datetime.now()
        user_results = UserSearchResults(
            username="testuser",
            start_time=start,
            end_time=end,
        )
        assert user_results.duration >= 0

    def test_user_search_results_get_found_results(self):
        """Test get_found_results method"""
        result1 = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
        )
        result2 = SearchResult(
            site="facebook",
            url="https://facebook.com/testuser",
            status=SearchStatus.NOT_FOUND,
        )
        user_results = UserSearchResults(
            username="testuser",
            results=[result1, result2],
        )
        found = user_results.get_found_results()
        assert len(found) == 1
        assert found[0].site == "twitter"

    def test_user_search_results_to_dict(self):
        """Test to_dict method"""
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
        )
        user_results = UserSearchResults(
            username="testuser",
            results=[result],
            total_sites_checked=1,
        )
        data = user_results.to_dict()
        assert data["username"] == "testuser"
        assert data["found_count"] == 1
        assert data["total_sites_checked"] == 1


@pytest.mark.unit
class TestSearchReport:
    """Test SearchReport dataclass"""

    def test_search_report_creation(self):
        """Test creating SearchReport"""
        report = SearchReport()
        assert report.total_users == 0
        assert report.total_accounts_found == 0
        assert report.success_rate == 0.0

    def test_search_report_add_user_results(self):
        """Test add_user_results method"""
        report = SearchReport()
        result = SearchResult(
            site="twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
        )
        user_results = UserSearchResults(
            username="testuser",
            results=[result],
            total_sites_checked=1,
        )
        report.add_user_results(user_results)
        assert report.total_users == 1
        assert report.total_accounts_found == 1
        assert report.total_sites_checked == 1

    def test_search_report_success_rate(self):
        """Test success_rate property"""
        report = SearchReport(total_sites_checked=100, total_accounts_found=50)
        assert report.success_rate == 50.0

    def test_search_report_success_rate_zero(self):
        """Test success_rate with zero total"""
        report = SearchReport()
        assert report.success_rate == 0.0

    def test_search_report_to_dict(self):
        """Test to_dict method"""
        report = SearchReport(
            total_users=1,
            total_sites_checked=10,
            total_accounts_found=5,
            total_errors=2,
        )
        data = report.to_dict()
        assert data["total_users"] == 1
        assert data["total_accounts_found"] == 5
        assert data["success_rate"] == 50.0
