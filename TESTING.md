# Testing Guide for CyberFind

## Overview

CyberFind uses pytest for comprehensive unit and integration testing. This guide covers how to run tests, understand test structure, and contribute new tests.

## Quick Start

### Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_rate_limiting.py

# Run specific test class
pytest tests/test_rate_limiting.py::TestRateLimiter

# Run specific test method
pytest tests/test_rate_limiting.py::TestRateLimiter::test_initialization
```

## Test Structure

### Directory Layout

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures and configuration
├── test_rate_limiting.py
├── test_proxy_support.py
├── test_batch_search.py
├── test_database_export.py
├── test_advanced_filter.py
├── test_reverse_search.py
├── test_account_age.py
├── test_custom_sites.py
├── test_performance_analytics.py
└── test_detailed_reports.py
```

### Test Modules

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_rate_limiting.py` | 17 | RateLimiter initialization, token acquisition, backoff strategies |
| `test_proxy_support.py` | 15 | ProxyManager initialization, proxy selection, statistics |
| `test_batch_search.py` | 25 | Batch operations, concurrency control, result filtering |
| `test_database_export.py` | 20 | Database operations, exports (CSV/JSON/HTML) |
| `test_advanced_filter.py` | 26 | Filtering, sorting, grouping, statistics |
| `test_reverse_search.py` | 24 | Fuzzy matching, variations, similarity detection |
| `test_account_age.py` | 24 | Account age analysis, bot/fake detection |
| `test_custom_sites.py` | 15 | Custom list management, merging, filtering |
| `test_performance_analytics.py` | 20 | Performance tracking, predictions, bottleneck detection |
| `test_detailed_reports.py` | 20 | Report generation (HTML/JSON/CSV/PDF) |

**Total: 186 test cases**

## Fixtures

Shared fixtures are defined in `conftest.py`:

```python
# Get project root
@pytest.fixture
def project_root():
    return Path(__file__).parent.parent

# Create test data directory
@pytest.fixture
def test_data_dir(project_root):
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    yield data_dir

# Temporary database
@pytest.fixture
def temp_db(tmp_path):
    return tmp_path / "test.db"

# Sample search result
@pytest.fixture
def sample_search_result():
    from cyberfind.core import SearchResult, Status
    return SearchResult(site="GitHub", url="https://github.com/testuser", 
                       username="testuser", status=Status.FOUND)

# Sample search results
@pytest.fixture
def sample_search_results():
    from cyberfind.core import SearchResult, Status
    return [
        SearchResult(site="GitHub", url="https://github.com/testuser", 
                    username="testuser", status=Status.FOUND),
        SearchResult(site="Twitter", url="https://twitter.com/testuser", 
                    username="testuser", status=Status.FOUND),
        SearchResult(site="LinkedIn", url="https://linkedin.com/in/testuser", 
                    username="testuser", status=Status.NOT_FOUND)
    ]

# Mock proxies
@pytest.fixture
def mock_proxies():
    return [
        "http://proxy1.com:8080",
        "http://proxy2.com:8080",
        "socks5://proxy3.com:1080"
    ]

# Mock sites
@pytest.fixture
def mock_sites():
    return [
        {"name": "GitHub", "url": "https://github.com/", "category": "programming", "priority": "9"},
        {"name": "Twitter", "url": "https://twitter.com/", "category": "social_media", "priority": "8"},
        {"name": "LinkedIn", "url": "https://linkedin.com/", "category": "professional", "priority": "7"}
    ]

# Mock usernames
@pytest.fixture
def mock_usernames():
    return ["alice", "bob", "charlie", "diana", "eve"]
```

## Running Tests with Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=cyberfind --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Coverage Goals

- **Minimum target**: 80% code coverage
- **Branch coverage**: Enabled in `.coveragerc`
- **Excluded patterns**: Tests, venv, pycache

## Test Markers

Tests are organized using pytest markers:

```python
@pytest.mark.unit          # Unit tests (default)
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Slow-running tests
@pytest.mark.performance   # Performance tests
@pytest.mark.asyncio       # Async tests
```

### Running Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run excluding slow tests
pytest -m "not slow"

# Run async tests
pytest -m asyncio
```

## Asynchronous Tests

Tests for async functions use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

The `asyncio_mode = auto` setting in `pytest.ini` automatically detects and handles async tests.

## Code Quality Checks

### Formatting with Black

```bash
# Format code
black cyberfind tests

# Check formatting
black --check cyberfind tests
```

### Import Sorting with isort

```bash
# Sort imports
isort cyberfind tests

# Check import sorting
isort --check-only cyberfind tests
```

### Linting with Flake8

```bash
# Run flake8
flake8 cyberfind tests

# Specific rules
flake8 cyberfind --max-line-length=120
```

### Type Checking with mypy

```bash
# Run type checker
mypy cyberfind

# Ignore missing imports
mypy cyberfind --ignore-missing-imports
```

## Running All Checks with Tox

```bash
# Test all Python versions
tox

# Test specific Python version
tox -e py311

# Run linting
tox -e lint

# Run type checking
tox -e type

# Run coverage
tox -e coverage
```

## Pre-commit Hooks

Setup pre-commit hooks to run checks before committing:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

Hooks configured in `.pre-commit-config.yaml`:
- Trailing whitespace
- File endings
- YAML validation
- Black formatting
- isort import sorting
- Flake8 linting
- mypy type checking
- Bandit security checks
- pylint analysis

## Continuous Integration

Tests automatically run on:
- **Push** to `main` or `develop` branches
- **Pull requests** to `main` or `develop`

GitHub Actions workflow (`.github/workflows/tests.yml`):
- Tests on Python 3.9, 3.10, 3.11
- Tests on Ubuntu, Windows, macOS
- Coverage reporting via Codecov
- Code quality checks (flake8, mypy, black, isort)
- Security scanning (bandit)

## Writing New Tests

### Test Template

```python
"""
Unit tests for new_module module
"""

import pytest
from cyberfind.new_module import NewClass


@pytest.mark.unit
class TestNewClass:
    """Test NewClass functionality"""

    def test_initialization(self):
        """Test class initialization"""
        obj = NewClass()
        
        assert obj.attribute == expected_value

    def test_method_with_fixture(self, sample_search_results):
        """Test method using fixture"""
        obj = NewClass()
        
        result = obj.method(sample_search_results)
        
        assert result is not None
```

### Best Practices

1. **Use descriptive names**: `test_filter_by_found()` not `test_1()`
2. **One assertion per test** (or related assertions)
3. **Use fixtures** for common test data
4. **Mock external dependencies**
5. **Test both happy path and edge cases**
6. **Use parametrize for multiple scenarios**

Example with parametrize:

```python
@pytest.mark.parametrize("input,expected", [
    ("found", True),
    ("not_found", False),
    ("error", None),
])
def test_status_parsing(input, expected):
    result = parse_status(input)
    assert result == expected
```

## Debugging Tests

### Running with Print Statements

```bash
# Show output from print statements
pytest -s test_file.py
```

### Running with Debugger

```bash
# Drop into pdb on failure
pytest --pdb test_file.py

# Drop into pdb on first failure and skip rest
pytest --pdbcls=IPython.terminal.debugger:TerminalPdb test_file.py
```

### Verbose Output

```bash
# Show test names and output
pytest -vv

# Show local variables in traceback
pytest -l
```

## Performance Testing

### Timing Tests

```bash
# Show slowest 10 tests
pytest --durations=10

# Mark slow tests
@pytest.mark.slow
def test_expensive_operation():
    ...

# Run only fast tests
pytest -m "not slow"
```

## Integration Testing

For integration tests that test multiple modules together:

```python
@pytest.mark.integration
class TestModuleIntegration:
    """Test interactions between modules"""
    
    def test_batch_search_with_database(self, temp_db):
        """Test batch search saving to database"""
        # Test multiple modules working together
        pass
```

## Troubleshooting

### Tests Not Discovered

```bash
# Check test discovery
pytest --collect-only

# Ensure test files start with test_
# Ensure test classes start with Test
# Ensure test methods start with test_
```

### Import Errors

```bash
# Check module imports
python -c "from cyberfind.module import Class"

# Install package in editable mode
pip install -e .
```

### Async Test Issues

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check asyncio_mode in pytest.ini
# Should be: asyncio_mode = auto
```

## Performance Optimization

When tests are slow:

1. **Use mocking** to avoid real network calls
2. **Use temp directories** instead of real databases
3. **Reduce data size** for test operations
4. **Mark slow tests** with `@pytest.mark.slow`
5. **Run in parallel**: `pytest -n auto` (requires pytest-xdist)

## Security Testing

```bash
# Run security checks
pytest --bandit

# Check for common vulnerabilities
bandit -r cyberfind
```

## Contributing Tests

When submitting PRs:

1. Write tests for new features
2. Ensure all tests pass: `pytest`
3. Run code quality checks: `tox`
4. Maintain 80%+ coverage
5. Use consistent style and naming

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures](https://docs.pytest.org/en/stable/how-to-use-fixtures.html)
- [pytest markers](https://docs.pytest.org/en/stable/example/markers.html)
- [Black code formatter](https://black.readthedocs.io/)
- [isort import sorting](https://pycqa.github.io/isort/)
- [mypy type checking](https://mypy.readthedocs.io/)

## Questions?

For questions about testing:
- Check existing tests in `tests/` directory
- Review pytest documentation
- Open an issue on GitHub

Happy testing! 🧪
