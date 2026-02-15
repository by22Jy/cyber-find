"""
Pytest configuration and fixtures for CyberFind tests
"""

import sys
from pathlib import Path
from typing import Generator

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get project root directory"""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get test data directory"""
    test_data = PROJECT_ROOT / "tests" / "data"
    test_data.mkdir(exist_ok=True)
    return test_data


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing"""
    db_path = tmp_path / "test.db"
    return str(db_path)


@pytest.fixture
def sample_search_result():
    """Create a sample SearchResult for testing"""
    from cyber_find.models import SearchResult, SearchStatus

    return SearchResult(
        site="GitHub",
        url="https://github.com/testuser",
        status=SearchStatus.FOUND,
        status_code=200,
        response_time=0.5,
        metadata={"followers": 100, "repos": 50},
    )


@pytest.fixture
def sample_search_results(sample_search_result):
    """Create multiple sample SearchResults"""
    from cyber_find.models import SearchResult, SearchStatus

    return [
        sample_search_result,
        SearchResult(
            site="Twitter",
            url="https://twitter.com/testuser",
            status=SearchStatus.FOUND,
            status_code=200,
            response_time=0.32,
            metadata={"followers": 500},
        ),
        SearchResult(
            site="LinkedIn",
            url="https://linkedin.com/in/testuser",
            status=SearchStatus.NOT_FOUND,
            status_code=404,
            response_time=0.2,
            error="Not found",
        ),
    ]


@pytest.fixture
def mock_proxies():
    """Get list of mock proxies"""
    return [
        "http://10.10.1.10:3128",
        "http://10.10.1.11:1080",
        "socks5://10.10.1.12:1080",
    ]


@pytest.fixture
def mock_sites():
    """Get list of mock sites"""
    return [
        {
            "name": "GitHub",
            "url": "https://github.com/",
            "category": "programming",
            "priority": "9",
        },
        {
            "name": "Twitter",
            "url": "https://twitter.com/",
            "category": "social_media",
            "priority": "8",
        },
        {
            "name": "LinkedIn",
            "url": "https://linkedin.com/",
            "category": "professional",
            "priority": "7",
        },
    ]


@pytest.fixture
def mock_usernames():
    """Get list of mock usernames"""
    return ["alice", "bob", "charlie", "diana", "eve"]


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "performance: mark test as a performance test")
    config.addinivalue_line("markers", "asyncio: mark test as using asyncio")


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add asyncio marker automatically for async tests
        if "asyncio" in item.keywords or "async_" in item.nodeid:
            item.add_marker(pytest.mark.asyncio)
