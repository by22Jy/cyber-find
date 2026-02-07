"""
Custom exceptions for CyberFind
"""


class CyberFindException(Exception):
    """Base exception for CyberFind"""

    pass


class ConfigurationError(CyberFindException):
    """Raised when configuration is invalid"""

    pass


class SiteListError(CyberFindException):
    """Raised when site list cannot be loaded"""

    pass


class SearchError(CyberFindException):
    """Raised when search operation fails"""

    pass


class DatabaseError(CyberFindException):
    """Raised when database operation fails"""

    pass


class APIError(CyberFindException):
    """Raised when API operation fails"""

    pass


class InvalidInputError(CyberFindException):
    """Raised when input validation fails"""

    pass


class TimeoutError(CyberFindException):
    """Raised when operation times out"""

    pass
