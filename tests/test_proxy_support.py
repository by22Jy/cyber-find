"""
Unit tests for proxy_support module
"""

import pytest

from cyber_find.proxy_support import ProxyManager


@pytest.mark.unit
class TestProxyManager:
    """Test ProxyManager functionality"""

    def test_initialization(self):
        """Test ProxyManager initialization"""
        mgr = ProxyManager()

        assert mgr.proxies == []
        assert mgr.current_index == 0
        assert mgr.failed_proxies == []

    def test_load_proxies_from_list(self, mock_proxies):
        """Test loading proxies from list"""
        mgr = ProxyManager()
        count = mgr.load_proxies_from_list(mock_proxies)

        assert count == 3
        assert len(mgr.proxies) == 3
        assert mgr.proxies == mock_proxies

    def test_load_proxies_empty_list(self):
        """Test loading empty list"""
        mgr = ProxyManager()
        count = mgr.load_proxies_from_list([])

        assert count == 0
        assert len(mgr.proxies) == 0

    def test_load_proxies_with_whitespace(self):
        """Test loading proxies with whitespace"""
        mgr = ProxyManager()
        proxies = ["  http://10.10.1.10:3128  ", "http://10.10.1.11:1080"]
        count = mgr.load_proxies_from_list(proxies)

        assert count == 2
        assert mgr.proxies[0] == "http://10.10.1.10:3128"

    def test_get_next_proxy_round_robin(self, mock_proxies):
        """Test round-robin proxy selection"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        p1 = mgr.get_next_proxy()
        p2 = mgr.get_next_proxy()
        p3 = mgr.get_next_proxy()
        p4 = mgr.get_next_proxy()

        assert p1 == mock_proxies[0]
        assert p2 == mock_proxies[1]
        assert p3 == mock_proxies[2]
        assert p4 == mock_proxies[0]

    def test_get_next_proxy_no_proxies(self):
        """Test getting next proxy when empty"""
        mgr = ProxyManager()

        proxy = mgr.get_next_proxy()
        assert proxy is None

    def test_get_random_proxy(self, mock_proxies):
        """Test random proxy selection"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        proxy = mgr.get_random_proxy()
        assert proxy in mock_proxies

    def test_report_success(self, mock_proxies):
        """Test success reporting"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        proxy = mock_proxies[0]
        mgr.report_success(proxy)

        stats = mgr.proxy_stats[proxy]
        assert stats["requests"] == 1
        assert stats["success"] == 1

    def test_report_failure(self, mock_proxies):
        """Test failure reporting"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        proxy = mock_proxies[0]
        mgr.report_failure(proxy)

        stats = mgr.proxy_stats[proxy]
        assert stats["requests"] == 1
        assert stats["failed"] == 1

    def test_success_rate_calculation(self, mock_proxies):
        """Test success rate calculation"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        proxy = mock_proxies[0]
        mgr.report_success(proxy)
        mgr.report_success(proxy)
        mgr.report_failure(proxy)

        stats = mgr.proxy_stats[proxy]
        assert stats["success_rate"] == pytest.approx(2 / 3)

    def test_get_best_proxy(self, mock_proxies):
        """Test getting best proxy"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        # Make first proxy best
        for _ in range(3):
            mgr.report_success(mock_proxies[0])

        best = mgr.get_best_proxy()
        assert best == mock_proxies[0]

    def test_remove_proxy(self, mock_proxies):
        """Test proxy removal"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        mgr.remove_proxy(mock_proxies[0])

        assert mock_proxies[0] not in mgr.proxies
        assert len(mgr.proxies) == 2

    def test_get_proxy_count(self, mock_proxies):
        """Test proxy count"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        mgr.report_failure(mock_proxies[0])

        count = mgr.get_proxy_count()
        assert count["total"] == 3
        assert count["available"] == 2
        assert count["failed"] == 1

    def test_clear_failed(self, mock_proxies):
        """Test clearing failed proxies"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        mgr.failed_proxies.append(mock_proxies[0])
        mgr.clear_failed()

        assert len(mgr.failed_proxies) == 0

    def test_get_proxy_stats(self, mock_proxies):
        """Test getting proxy statistics"""
        mgr = ProxyManager()
        mgr.load_proxies_from_list(mock_proxies)

        mgr.report_success(mock_proxies[0])

        stats = mgr.get_proxy_stats()
        assert mock_proxies[0] in stats
        assert stats[mock_proxies[0]]["success"] == 1
