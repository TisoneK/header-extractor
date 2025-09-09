from setuptools import setup, find_packages
from pathlib import Path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Get package directory
package_dir = Path("header_extractor")

setup(
    name="header-extractor",
    version="1.1.0",  # Bump version for config changes
    author="Tisone Kironget",
    author_email="tisonkironget@gmail.com",
    description="A simple tool to extract HTTP headers from web pages with configurable settings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TisoneK/header-extractor",
    packages=find_packages(),
    package_data={
        'header_extractor': ['config/*.json'],
    },
    include_package_data=True,
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "header-extractor=header_extractor.cli:main",
        ],
    },
    keywords="http headers extractor web scraping",
    project_urls={
        "Bug Reports": "https://github.com/TisoneK/header-extractor/issues",
        "Source": "https://github.com/TisoneK/header-extractor",
    },
)