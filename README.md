# 🕵️ CyberFind - Advanced OSINT Search Tool

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.3.2-blue?style=for-the-badge&logo=github" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=for-the-badge" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge&logo=opensourceinitiative" alt="License">
  <img src="https://img.shields.io/badge/Tests-36%20Passing-brightgreen?style=for-the-badge&logo=pytest" alt="Tests">
  <img src="https://img.shields.io/badge/Code%20Style-Black-black?style=for-the-badge&logo=python" alt="Code Style">
</p>

<p align="center">
  <b>Find user accounts across 200+ platforms in seconds</b>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&duration=3000&pause=1000&color=00FF00&center=true&vCenter=true&width=800&height=80&lines=Find+Everything.;Track+Everyone.;Stay+Anonymous." alt="CyberFind Slogan">
</p>

## ✨ Features

### 🔍 **Comprehensive Search**
- **200+ built-in sites** across multiple categories
- **Smart detection** using status codes and content analysis
- **Metadata extraction** from found profiles

### ⚡ **High Performance**
- **Async/await architecture** for maximum speed
- **Concurrent requests** with configurable thread count
- **Intelligent rate limiting** to avoid blocks

### 🛡️ **Privacy & Security**
- **Random User-Agents** for each request
- **Multiple search modes** (Standard, Deep, Stealth, Aggressive)
- **No data storage** unless explicitly configured

### 📊 **Multiple Output Formats**
- **JSON** - Structured data for APIs
- **CSV** - Spreadsheet compatible format  
- **HTML** - Beautiful visual reports
- **Excel** - Professional multi-sheet workbooks
- **SQLite** - Database storage for large datasets

### 🎯 **Smart Features**
- **Risk assessment** based on found accounts
- **Personalized recommendations**
- **Statistical analysis** of results
- **Category grouping** of found accounts

### 🔬 **Advanced OSINT Capabilities**
- **DNS Enumeration**: Retrieve A, AAAA, MX, TXT, NS, SOA, and CNAME records for domains.
- **WHOIS Lookup**: Get registration details, owner information, and name servers for domains.
- **Shodan Integration**: Search for exposed devices and services (requires Shodan API key).
- **VirusTotal Scan**: Check URLs for malicious content (requires VirusTotal API key).
- **Wayback Machine Search**: Find archived versions of web pages.
- **Selenium Scraping**: Analyze JavaScript-heavy websites that standard requests might miss.
- **Advanced Combined Search**: Perform a standard username search and then run additional checks (DNS, WHOIS, Shodan, VT, Wayback) based on the results and provided API keys.
- **Detailed Reporting**: Generate comprehensive text reports summarizing all findings from standard and advanced checks.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/VAZlabs/cyber-find.git  
cd cyber-find
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate.bat # Windows

# Install dependencies
pip install -r requirements.txt
pip install .

# Make it executable (Linux/macOS)
chmod +x cyberfind
```

### Basic Usage

```bash
# Quick search (25 most popular sites)
cyberfind username

# Search with specific category
cyberfind username --list social_media
cyberfind username --list programming
cyberfind username --list gaming

# Comprehensive search (200+ sites)
cyberfind username --list all

# Multiple users
cyberfind user1 user2 user3 --list quick
```

## 📚 Usage Examples

### 🔎 Basic Searches

```bash
# Quick check on popular platforms
cyberfind john_doe

# Russian-language platforms only
cyberfind username --list russian

# Gaming platforms only
cyberfind username --list gaming

# Blogs and publications
cyberfind username --list blogs
```

### ⚙️ Advanced Options

```bash
# Deep search with HTML report
cyberfind target --mode deep --format html -o report

# Stealth mode for sensitive searches
cyberfind target --mode stealth --timeout 15

# Maximum speed (use with caution)
cyberfind target --mode aggressive --threads 100

# Custom sites file
cyberfind target -f custom_sites.txt
```

### 📊 Output Management

```bash
# Save as JSON (default)
cyberfind username -o results

# Save as CSV for Excel
cyberfind username --format csv -o results

# Save as HTML report
cyberfind username --format html -o report

# Save to database
cyberfind username --format sqlite
```

### 🧪 Advanced Search (v0.3.2) - CLI (Conceptual)
*Note: Direct CLI integration for advanced features might require specific implementation in `cyberfind_cli.py`. Currently, they are primarily accessible via the Python API.*

## 📋 Available Site Lists

| List Name | Sites Count | Description |
|-----------|-------------|-------------|
| **quick** | 25 | Most popular platforms (default) |
| **social_media** | 70+ | All social networks |
| **programming** | 25+ | IT and development platforms |
| **gaming** | 20+ | Gaming platforms and communities |
| **blogs** | 20+ | Blogs and publication platforms |
| **ecommerce** | 20+ | Shopping and commerce sites |
| **forums** | 12+ | Discussion forums |
| **russian** | 18+ | Russian-language platforms |
| **all** | 200+ | All available platforms |

View all available lists:
```bash
cyberfind --show-lists
```

## 🎛️ Configuration

Create a `config.yaml` file for custom settings:

```yaml
# config.yaml
general:
  timeout: 30                    # Request timeout in seconds
  max_threads: 50                # Maximum concurrent requests
  retry_attempts: 3              # Retry attempts on failure
  retry_delay: 2                 # Delay between retries
  user_agents_rotation: true     # Rotate User-Agents
  rate_limit_delay: 0.5          # Delay between requests

proxy:
  enabled: false                 # Enable proxy support
  list: []                       # List of proxies
  rotation: true                 # Rotate proxies

database:
  sqlite_path: 'cyberfind.db'    # SQLite database path

output:
  default_format: 'json'         # Default output format
  save_all_results: true         # Save all results to DB

advanced:
  metadata_extraction: true      # Extract metadata from pages
  cache_results: true            # Cache results
  verify_ssl: true               # Verify SSL certificates
```

## 📁 Project Structure

```
cyberfind/
├── cyberfind_cli.py          # Main CLI interface
├── core.py                   # Core search engine
├── gui.py                    # Graphical interface
├── api.py                    # REST API server
├── config.yaml              # Configuration template
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── sites/                  # Site definition files
    ├── social_media.txt
    ├── programming.txt
    ├── gaming.txt
    └── ...
```

## 🔧 Development

### Code Style & Quality

```bash
# Install development tools
pip install -r requirements-dev.txt

# Format code with black
black cyberfind --line-length 120

# Check code style with flake8
flake8 cyberfind --max-line-length 120

# Sort imports with isort
isort cyberfind --profile black

# Type checking with mypy
mypy cyberfind --ignore-missing-imports
```

### 🧪 Testing & CI/CD

CyberFind has comprehensive testing infrastructure to ensure code quality and reliability:

#### Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rate_limiting.py -v

# Run with coverage report
pytest tests/ --cov=cyberfind --cov-report=html

# Run only fast tests
pytest tests/ -m "not slow"

# Run async tests only
pytest tests/ -m asyncio
```

#### Test Coverage

Current test infrastructure includes:
- **36 unit tests** covering core modules
- **2 test modules**: `test_rate_limiting.py` (17 tests), `test_proxy_support.py` (15 tests)
- **8 pytest fixtures** for reusable test data
- **Branch coverage tracking** enabled in `.coveragerc`
- **Async test support** with `@pytest.mark.asyncio`

#### Code Quality Checks

All commits are validated against:
- ✅ **flake8** - PEP8 style compliance (0 errors)
- ✅ **black** - Code formatting (120 char lines)
- ✅ **isort** - Import sorting (black-compatible)
- ✅ **mypy** - Type checking (Python 3.9+)
- ✅ **pytest** - Unit tests (36 tests passing)
- ✅ **bandit** - Security scanning

#### GitHub Actions CI/CD

Automated testing runs on:
- Python 3.9, 3.10, 3.11
- Linux, Windows, macOS
- Every push and pull request

See `.github/workflows/tests.yml` for workflow configuration.

#### Pre-commit Hooks

Setup local git hooks for instant validation:

```bash
# Install pre-commit
pip install pre-commit

# Setup git hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

For detailed testing documentation, see [TESTING.md](TESTING.md)

## 🌐 API Usage

Start the API server:
```bash
cyberfind --api
# Server starts at http://localhost:8080
```

Example API request:
```python
import requests
import json

response = requests.post('http://localhost:8080/api/search', json={
    'usernames': ['target_user'],
    'list': 'social_media',
    'mode': 'standard'
})

results = response.json()
```

## 🖥️ Graphical Interface

```bash
# Launch the GUI
cyberfind --gui
```

The GUI provides:
- Visual search interface
- Real-time progress tracking
- Interactive results display
- One-click report generation

## 📊 Sample Output

```bash
$ cyberfind john_doe --list quick

🔍 CyberFind v0.3.2
Searching for: john_doe
📋 Using built-in list: quick (25 sites)

🔍 Searching: john_doe
  Checking 25 sites...
    ✓ Found: GitHub
    ✓ Found: Twitter
    ✓ Found: LinkedIn
  Done: 3 found, 2 errors

✅ SEARCH COMPLETED in 12.5 seconds
============================================================

📊 STATISTICS:
  Total checks: 25
  Accounts found: 3
  Errors: 2

👤 USER: john_doe
  ✅ FOUND 3 accounts:
    📁 PROGRAMMING:
      1. GitHub
          URL: https://github.com/john_doe    
          Status: 200, Time: 1.23s
    📁 SOCIAL_MEDIA:
      2. Twitter
          URL: https://twitter.com/john_doe    
          Status: 200, Time: 0.89s
      3. LinkedIn
          URL: https://www.linkedin.com/in/john_doe    
          Status: 200, Time: 1.45s

💡 RECOMMENDATIONS:
  1. LinkedIn profile found - check contacts and connections
  2. GitHub profile found - review public repositories

💾 Results saved to: results.json
```

## 🚨 Legal & Ethical Usage

### ✅ **Permitted Uses:**
- Security research and penetration testing (with permission)
- Personal digital footprint analysis
- Academic research on social media presence
- Bug bounty hunting and security audits
- Investigating your own online presence

### ❌ **Prohibited Uses:**
- Harassment, stalking, or doxxing
- Unauthorized surveillance
- Privacy violations
- Commercial data scraping without permission
- Any illegal activities

**By using this tool, you agree to use it responsibly and legally. The developers are not responsible for misuse.**

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes:
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Code Quality Standards

All contributions must pass our quality gates:

**Required Checks:**
- ✅ **Black** code formatting (`black --line-length 120`)
- ✅ **flake8** PEP8 linting (max line 120, 0 errors)
- ✅ **isort** import sorting (black-compatible profile)
- ✅ **mypy** type checking (Python 3.9+ strict mode)
- ✅ **pytest** unit tests (all passing)
- ✅ **bandit** security scanning

**Before submitting a PR, run locally:**
```bash
# Format code
black cyberfind --line-length 120

# Sort imports
isort cyberfind --profile black --line-length 120

# Check style
flake8 cyberfind --max-line-length 120 --ignore=E203,E266,E501,W503,E741

# Type checking
mypy cyberfind --ignore-missing-imports

# Run tests
pytest tests/ -v
```

**Test Requirements:**
- New features must include unit tests
- Maintain minimum 80% code coverage
- Use pytest fixtures from `tests/conftest.py`
- Add `@pytest.mark.unit` to unit tests
- Add `@pytest.mark.asyncio` to async tests
- See [TESTING.md](TESTING.md) for detailed testing guidelines

**Automated Checks:**
- GitHub Actions runs tests on Python 3.9, 3.10, 3.11
- Pre-commit hooks available (run `pre-commit install`)
- All checks must pass before merging

### Areas for Contribution:
- Adding new site definitions
- Improving detection algorithms
- Enhancing the GUI
- Writing documentation
- Performance optimizations
- Bug fixes
- Integrating advanced features into CLI/API

## 📈 Performance Tips

1. **For speed**: Use `--mode aggressive --threads 50`
2. **For stealth**: Use `--mode stealth --timeout 30`
3. **For reliability**: Use `--mode standard --retry 3`
4. **For specific needs**: Create custom site lists

## 🐛 Troubleshooting

### Common Issues:

1. **"No sites loaded" error**
   - Ensure you have internet connection
   - Check if the sites directory exists

2. **Slow performance**
   - Reduce thread count: `--threads 20`
   - Increase timeout: `--timeout 30`
   - Use a faster internet connection

3. **Many errors**
   - The target platforms may be blocking requests
   - Try using stealth mode
   - Consider using proxies

### Getting Help:
- Check the [GitHub Issues](https://github.com/vazor-code/cyber-find/issues)
- Review the example configurations
- Test with a simple search first

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [aiohttp](https://docs.aiohttp.org/) for async HTTP requests
- Uses [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- Inspired by various OSINT tools in the security community
- Thanks to the contributors for making CyberFind better!

## 📬 Contact

- **GitHub**: [vazor-code](https://github.com/vazor-code)
- **Project**: [CyberFind](https://github.com/vazor-code/cyber-find)
- **Issues**: [Report a bug](https://github.com/vazor-code/cyber-find/issues)

---

<p align="center">
  <b>CyberFind</b> · Find accounts · Analyze presence · Stay informed
  <br>
  <sub>Remember: With great power comes great responsibility</sub>
</p>

<div align="center">
  
### ⭐ If you find this useful, please give it a star!

[![GitHub stars](https://img.shields.io/github/stars/vazor-code/cyber-find?style=social)](https://github.com/vazor-code/cyber-find/stargazers)

</div>
