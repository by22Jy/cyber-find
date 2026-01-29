#!/usr/bin/env python3
from setuptools import setup, find_packages

# Определение основных зависимостей (включая v0.2.1)
install_requires = [
    # Core OSINT & Web Scraping
    "aiohttp>=3.9.1",
    "beautifulsoup4>=4.12.2",
    "cloudscraper>=1.2.71",
    "fake-useragent>=1.4.0",
    "requests>=2.31.0",
    "lxml>=4.9.3",                     

    # Data Handling & Output
    "pandas>=2.1.4",
    "PyYAML>=6.0.1",
    "openpyxl>=3.1.2", 
    "xlsxwriter>=3.1.0", 
    "tabulate>=0.9.0", 

    # GUI
    "customtkinter>=5.2.0",
    "pillow>=10.0.0", 

    # API & Web Server
    "fastapi>=0.104.1",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",

    # New dependencies for v0.2.1 features
    "dnspython>=2.4.2",
    "python-whois>=0.8.0",
    "shodan>=1.29.0",
    "virustotal-python>=0.16.0", # Важно: virustotal-python, а не virustotal-api
    "censys>=2.2.3",
    "waybackpy>=3.0.6",
    "selenium>=4.15.0",
    "validators>=0.22.0",
    "tqdm>=4.66.1",
    "colorama>=0.4.6",

    # Other
    "importlib-resources>=5.10.0",
]

# Определение зависимостей для разработки
extras_require = {
    'dev': [
        'pytest>=7.4.3',
        'pytest-asyncio>=0.21.1',
        'pytest-cov>=4.1.0',
        'black>=23.11.0',
        'flake8>=6.1.0',
        'mypy>=1.7.1',
        'types-requests>=2.31.0.6',
        'types-PyYAML>=6.0.12.12',
        'types-tabulate>=0.9.0.5',
        'types-beautifulsoup4>=4.12.0.2',
        'types-openpyxl>=3.1.2.2',
        # Добавьте другие зависимости для разработки по необходимости
    ]
}

setup(
    name="cyberfind",
    version="0.2.1",
    author="VAZlabs",
    author_email="vazorcode@gmail.com",
    description="Advanced OSINT tool for searching users across platforms",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/VAZlabs/cyber-find",
    packages=find_packages(),
    package_data={
        'cyberfind': ['sites/*.txt'],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "cyberfind=cyberfind.cli:main",
            "cyberfind-gui=cyberfind.gui_main:main",
            "cyberfind-api=cyberfind.api_main:main",
        ],
    },
)