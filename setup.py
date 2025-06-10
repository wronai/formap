#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for Formap."""

import os
import re
from setuptools import setup, find_packages

# Read the version from the package
with open(os.path.join("formap", "__init__.py"), "r", encoding="utf-8") as f:
    version = re.search(
        r'^__version__\s*=\s*["\']([^"\']+)["\']',
        f.read(),
        re.MULTILINE,
    ).group(1)

# Read the README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip()]

setup(
    name="formap",
    version=version,
    description="Advanced form mapping and auto-filling tool with LLM integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    url="https://github.com/softreck/formap",
    packages=find_packages(include=["formap", "formap.*"]),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "formap=formap.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    keywords="form automation playwright testing web-scraping",
    project_urls={
        "Bug Reports": "https://github.com/softreck/formap/issues",
        "Source": "https://github.com/softreck/formap",
    },
)
