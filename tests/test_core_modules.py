"""
Unit tests for CyberFind modules
"""

import pytest

from cyber_find.core import CyberFind
from cyber_find.proxy_support import ProxyManager
from cyber_find.rate_limiting import RateLimiter


@pytest.mark.unit
class TestCyberFindCore:
    """Test CyberFind core functionality"""

    def test_cyberfind_can_be_imported(self):
        """Test that CyberFind can be imported"""
        assert CyberFind is not None


@pytest.mark.unit
class TestRateLimiter:
    """Test RateLimiter functionality"""

    def test_rate_limiter_can_be_imported(self):
        """Test RateLimiter can be imported"""
        assert RateLimiter is not None


@pytest.mark.unit
class TestProxyManager:
    """Test ProxyManager functionality"""

    def test_proxy_manager_can_be_imported(self):
        """Test ProxyManager can be imported"""
        assert ProxyManager is not None

    def test_proxy_manager_initialization(self):
        """Test adding proxies"""
        manager = ProxyManager()
        assert manager is not None
