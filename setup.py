#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="cyberfind",
    version="0.2.0",
    author="vazor",
    author_email="vazorcode@gmail.com",
    description="Advanced OSINT tool for searching users across platforms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vazor-code/cyber-find",
    packages=find_packages(),
    package_data={
        'cyberfind': ['sites/*.txt'],
    },
    py_modules=['cyberfind_cli', 'cyberfind_gui', 'cyberfind_api'],
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
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.9.1",
        "beautifulsoup4>=4.12.2",
        "cloudscraper>=1.2.71",
        "fake-useragent>=1.4.0",
        "pandas>=2.1.4",
        "PyYAML>=6.0.1",
        "requests>=2.31.0",
        "openpyxl>=3.1.2",
        "customtkinter>=5.2.0",
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "cyberfind=cyberfind_cli:main",
            "cyberfind-gui=cyberfind_gui:main",
            "cyberfind-api=cyberfind_api:main",
        ],
    },
)