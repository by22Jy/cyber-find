# 🤝 Contributing to CyberFind

<p align="center">
  <img src="https://img.shields.io/badge/Version-0.2.0-blue?style=for-the-badge&logo=github        " alt="Version">
  <img src="https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python        " alt="Python">
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=for-the-badge        " alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-red?style=for-the-badge&logo=opensourceinitiative        " alt="License">
</p>

<p align="center">
  <b>Find user accounts across 200+ platforms in seconds</b>
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&duration=3000&pause=1000&color=00FF00&center=true&vCenter=true&width=800&height=80&lines=Join+the+Mission.;Build+the+Future.;Stay+Ethical." alt="CyberFind Slogan">
</p>

## 🎯 Table of Contents

- [🚀 Getting Started](#-getting-started)
- [📋 Prerequisites](#-prerequisites)
- [🔧 Development Setup](#-development-setup)
- [🐛 How to Contribute](#-how-to-contribute)
- [🎨 Code Style](#-code-style)
- [🧪 Testing](#-testing)
- [📝 Pull Request Process](#-pull-request-process)
- [💬 Community](#-community)
- [🙏 Thank You](#-thank-you)

---

## 🚀 Getting Started

Thank you for your interest in contributing to **CyberFind**! We're thrilled that you want to join our mission to build the most advanced OSINT tool available. Whether you're fixing a bug, adding a new feature, improving documentation, or enhancing the user experience, your contribution is valuable.

### 🤔 Ways to Contribute

- 🐛 **Bug Reports**: Help us identify and squash bugs
- ✨ **Feature Requests**: Suggest new capabilities
- 🔧 **Code Contributions**: Add features, fix issues, optimize performance
- 📚 **Documentation**: Improve README, guides, and examples
- 🌐 **Translations**: Make CyberFind accessible worldwide
- 🧪 **Testing**: Write and improve test suites
- 🎨 **UI/UX**: Enhance the graphical interface
- 🐙 **Site Definitions**: Add new platforms to our database

---

## 📋 Prerequisites

Before you start contributing, please ensure you have:

- [Python 3.8+](https://www.python.org/downloads/) installed
- [Git](https://git-scm.com/downloads) installed
- Familiarity with [GitHub workflows](https://guides.github.com/introduction/flow/)
- Understanding of [async/await concepts](https://realpython.com/async-io-python/)
- Knowledge of [HTTP status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) (for site definitions)
- A passion for cybersecurity and OSINT!

---

## 🔧 Development Setup

### 1. Fork the Repository

Click the **Fork** button in the top-right corner of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/VAZlabs/cyber-find.git  
cd cyber-find
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools
```

### 5. Install in Editable Mode

```bash
pip install -e .
```

### 6. Create a Branch

```bash
git checkout -b feature/your-amazing-feature
```

---

## 🐛 How to Contribute

### 🐞 Reporting Bugs

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** with the `bug` label
3. **Include detailed information**:
   - OS and Python version
   - CyberFind version
   - Steps to reproduce
   - Expected vs. actual behavior
   - Error messages and logs

### 💡 Suggesting Features

1. **Check if it's already requested** in issues
2. **Open a feature request** with the `enhancement` label
3. **Provide context**:
   - What problem does it solve?
   - How should it work?
   - Are there similar implementations elsewhere?

### 🔨 Code Contributions

1. **Find an issue** or create your own
2. **Comment** that you're working on it
3. **Follow the development setup** above
4. **Write clean, well-documented code**
5. **Test your changes thoroughly**
6. **Submit a pull request**

---

## 🎨 Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) guidelines
- Use [Black](https://github.com/ambv/black) for code formatting
- Use [Flake8](https://flake8.pycqa.org/) for linting
- Use [isort](https://pycqa.github.io/isort/) for import sorting

### Commands to Run

```bash
# Format code
black cyberfind/

# Sort imports
isort cyberfind/

# Lint code
flake8 cyberfind/

# Run all formatters
black cyberfind/ && isort cyberfind/ && flake8 cyberfind/
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after a blank line

```bash
git commit -m "Brief summary of changes

More detailed explanatory text, if necessary. The blank line separating
the summary from the body is critical (unless you omit the body entirely).
Explain the problem that this commit is solving. Focus on why you are
making this change as opposed to how (the code explains how).
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=cyberfind tests/

# Run specific test file
pytest tests/test_core.py

# Run with verbose output
pytest -v tests/
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test function names
- Follow the `test_` prefix convention
- Test both success and failure scenarios
- Use `pytest` fixtures for setup/teardown

### Example Test

```python
def test_username_validation():
    """Test that invalid usernames are properly rejected."""
    assert validate_username("valid_user") == True
    assert validate_username("") == False
    assert validate_username("user@invalid") == False
```

---

## 📝 Pull Request Process

### 1. Before Submitting

- Ensure all tests pass
- Run code formatters (black, isort, flake8)
- Update documentation if needed
- Add tests for new features
- Squash commits if necessary

### 2. Creating the PR

- Go to the original repository
- Click "New Pull Request"
- Select your branch
- Fill out the template (if available)
- Provide a clear title and description

### 3. PR Template

```markdown
## Summary

Brief description of changes made.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

Describe how you tested your changes.

## Checklist

- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code
- [ ] I have made corresponding changes to documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective
```

### 4. After Submission

- Respond to feedback promptly
- Make requested changes
- Be patient—reviews take time
- Celebrate your contribution! 🎉

---

## 💬 Community

### Need Help?

- **Discussions**: [CyberFind Discussions](https://github.com/vazor-code/cyber-find/discussions      )
- **Issues**: [GitHub Issues](https://github.com/vazor-code/cyber-find/issues      )
- **Email**: [vazorcode@gmail.com]

### Code of Conduct

Please read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md). We expect all contributors to be respectful and inclusive.

---

## 🙏 Thank You

<div align="center">

**Your contributions make CyberFind stronger and more useful for the entire OSINT community. Thank you for helping us build tools that empower ethical investigation and cybersecurity research.**

<br>

[![](https://contrib.rocks/image?repo=vazor-code/cyber-find      )](https://github.com/vazor-code/cyber-find/graphs/contributors      )

<br>

### ⭐ Don't forget to star the repo if you enjoyed contributing!

</div>

---

<div align="center">

Made with ❤️ by the CyberFind Community

</div>
