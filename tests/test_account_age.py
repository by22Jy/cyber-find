"""
Unit tests for account_age module
"""

import pytest

from cyberfind.account_age import AccountAgeDetector


@pytest.mark.unit
class TestAccountAgeDetector:
    """Test AccountAgeDetector functionality"""

    def test_detector_exists(self):
        """Test that detector class exists"""
        assert AccountAgeDetector is not None

    def test_static_method_estimate(self, sample_search_result):
        """Test account age estimation"""
        result = AccountAgeDetector.estimate_account_age(sample_search_result)
        # Result should be either a dict or None
        assert result is None or isinstance(result, dict)
