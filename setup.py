#!/usr/bin/env python3
"""
Setup script for AI-Powered Media Library Organizer

This script allows the package to be installed using pip install.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements from requirements.txt
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ai-media-organizer",
    version="1.0.0",
    author="Media Organizer Team",
    author_email="contact@example.com",
    description="AI-powered media library organizer using Google Gemini",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-media-organizer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "media-organizer=main:cli",
            "organize-media=main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.example"],
    },
    zip_safe=False,
    keywords=[
        "media",
        "organizer",
        "tv shows",
        "movies",
        "ai",
        "gemini",
        "automation",
        "file management",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ai-media-organizer/issues",
        "Source": "https://github.com/yourusername/ai-media-organizer",
        "Documentation": "https://github.com/yourusername/ai-media-organizer#readme",
    },
)
