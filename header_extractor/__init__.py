"""
Header Extractor

A tool to extract and analyze HTTP headers from web requests.

Example usage:
    >>> from header_extractor import HeaderExtractor
    >>> extractor = HeaderExtractor()
    >>> result = extractor.extract_request_headers('https://example.com')
    >>> print(result)
"""

from .main import HeaderExtractor
from .config import get_config, update_config

__version__ = "1.1.0"
__author__ = "Tisone Kironget"
__email__ = "tisonkironget@gmail.com"

__all__ = [
    'HeaderExtractor',
    'get_config',
    'update_config',
    '__version__',
    '__author__',
    '__email__'
]