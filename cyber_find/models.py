"""
Search result models and utilities for CyberFind
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SearchStatus(Enum):
    """Status of search result"""

    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class SearchResult:
    """Single search result for a platform"""

    site: str
    url: str
    status: SearchStatus
    status_code: Optional[int] = None
    response_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    # Additional fields for extended functionality
    username: Optional[str] = None
    confidence: int = 0
    category: Optional[str] = None
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @property
    def is_success(self) -> bool:
        """Check if search was successful"""
        return self.status == SearchStatus.FOUND

    @property
    def found(self) -> bool:
        """Alias for is_success - check if account was found"""
        return self.is_success

    @property
    def site_name(self) -> str:
        """Alias for site name"""
        return self.site


@dataclass
class UserSearchResults:
    """Results for a single user search"""

    username: str
    results: List[SearchResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_sites_checked: int = 0
    error_count: int = 0

    @property
    def found_count(self) -> int:
        """Count of found accounts"""
        return sum(1 for r in self.results if r.is_success)

    @property
    def not_found_count(self) -> int:
        """Count of not found accounts"""
        return sum(1 for r in self.results if r.status == SearchStatus.NOT_FOUND)

    @property
    def duration(self) -> float:
        """Duration of search in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def get_found_results(self) -> List[SearchResult]:
        """Get only found results"""
        return [r for r in self.results if r.is_success]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "username": self.username,
            "found_count": self.found_count,
            "not_found_count": self.not_found_count,
            "error_count": self.error_count,
            "total_sites_checked": self.total_sites_checked,
            "duration": self.duration,
            "results": [r.to_dict() for r in self.results],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


@dataclass
class SearchReport:
    """Report for complete search operation"""

    total_users: int = 0
    total_sites_checked: int = 0
    total_accounts_found: int = 0
    total_errors: int = 0
    duration: float = 0.0
    user_results: Dict[str, UserSearchResults] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Success rate as percentage"""
        if self.total_sites_checked == 0:
            return 0.0
        return (self.total_accounts_found / self.total_sites_checked) * 100

    def add_user_results(self, user_results: UserSearchResults) -> None:
        """Add results for a user"""
        self.user_results[user_results.username] = user_results
        self.total_users = len(self.user_results)
        self.total_accounts_found += user_results.found_count
        self.total_sites_checked += user_results.total_sites_checked
        self.total_errors += user_results.error_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_users": self.total_users,
            "total_sites_checked": self.total_sites_checked,
            "total_accounts_found": self.total_accounts_found,
            "total_errors": self.total_errors,
            "duration": self.duration,
            "success_rate": self.success_rate,
            "user_results": {
                username: results.to_dict() for username, results in self.user_results.items()
            },
        }
