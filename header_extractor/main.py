#!/usr/bin/env python3
"""
Header Extractor - Main Module

This module provides the HeaderExtractor class to extract HTTP request headers.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from bs4 import BeautifulSoup

from .config import get_config


class HeaderExtractor:
    """A class to extract request headers sent to web pages."""

    def __init__(self, timeout: Optional[int] = None, 
                 custom_headers: Optional[Dict[str, str]] = None,
                 output_dir: Optional[Union[str, Path]] = None):
        """Initialize the HeaderExtractor.
        
        Args:
            timeout: Request timeout in seconds. Uses config value if None.
            custom_headers: Custom headers to use. Will override defaults.
            output_dir: Custom output directory for saved files. Uses config value if None.
        """
        # Get current configuration
        self.config = get_config()
        
        # Initialize session with default timeout
        self.session = requests.Session()
        self.timeout = timeout or self.config['default_timeout']
        
        # Set output directory (use provided, then config, default to 'output')
        self.output_dir = self._setup_output_dir(output_dir)
        
        # Set default headers from config
        self.session.headers.update(self.config['default_headers'])
        
        # Add custom headers if provided
        if custom_headers:
            self.session.headers.update(custom_headers)
        
        # Ensure output directory exists if needed
        if self.config['auto_create_output_dir']:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_output_dir(self, output_dir: Optional[Union[str, Path]] = None) -> Path:
        """Setup the output directory.
        
        Args:
            output_dir: Custom output directory. Uses config value if None.
            
        Returns:
            Path: The output directory path
        """
        if output_dir is not None:
            return Path(output_dir)
        return Path(self.config.get('output_dir', 'output'))
    
    def set_output_dir(self, output_dir: Union[str, Path]) -> None:
        """Set a new output directory.
        
        Args:
            output_dir: New output directory path
            
        Note:
            The directory will be created if it doesn't exist and auto_create_output_dir is True.
        """
        self.output_dir = Path(output_dir)
        if self.config['auto_create_output_dir']:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_domain(self, url: str) -> str:
        """Extract and clean domain from URL.
        
        Args:
            url: The URL to extract domain from
            
        Returns:
            Cleaned domain string
        """
        # Remove protocol and path
        domain = url.split('//')[-1].split('/')[0]
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Remove port if present
        domain = domain.split(':')[0]
        
        return domain
        
    def save_to_file(self, data: dict, filename: Optional[str] = None, 
                   output_dir: Optional[Union[str, Path]] = None) -> str:
        """Save data to a JSON file in the output directory.
        
        Args:
            data: Data to save as JSON. Should contain 'url' key for filename generation.
            filename: Output filename. If None, generates a name in format 'headers_<domain>_<date>.json'
            output_dir: Output directory. Uses instance output_dir if None.
                      Set via constructor or set_output_dir().
            
        Returns:
            Path to the saved file as a string
            
        Example:
            # Basic usage
            extractor = HeaderExtractor()  # Uses default output_dir from config
            extractor.save_to_file(data)
            
            # Custom output directory (temporary for this call)
            extractor.save_to_file(data, output_dir='custom/path')
            
            # Change default output directory for all future calls
            extractor.set_output_dir('data/headers')
            extractor.save_to_file(data)
        """
        output_dir = Path(output_dir) if output_dir is not None else self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not filename:
            # Get current date and time in YYYY_MMDD_HHMM format
            datetime_str = time.strftime("%Y_%m%d_%H%M")
            
            # Extract domain from URL in data or use 'unknown'
            domain = 'unknown'
            if isinstance(data, dict) and 'url' in data:
                try:
                    domain = self._extract_domain(data['url'])
                except Exception:
                    pass
                    
            filename = f"headers_{domain}_{datetime_str}.json"
        
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return str(output_path)
        
    def extract_request_headers(self, url: str, 
                             custom_headers: Optional[Dict[str, str]] = None,
                             use_comprehensive: bool = False) -> Dict[str, any]:
        """Extract request headers that would be sent to the given URL.
        
        Args:
            url: The URL to extract headers for
            custom_headers: Custom headers to include
            use_comprehensive: Whether to use comprehensive headers
            
        Returns:
            Dictionary containing request headers and status
        """
        try:
            # Ensure URL has a scheme
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # Use comprehensive headers if requested and no custom headers provided
            headers = {}
            if use_comprehensive and not custom_headers:
                headers.update(self.config['comprehensive_headers'])
            if custom_headers:
                headers.update(custom_headers)
            
            # Prepare the request
            req = requests.Request('GET', url, headers=headers)
            prepared = self.session.prepare_request(req)
            
            return {
                'url': url,
                'request_headers': dict(prepared.headers),
                'status': 'prepared'
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'request_headers': {},
                'status': 'error'
            }
            
    def send_request_and_capture_headers(self, url: str, 
                                      custom_headers: Optional[Dict[str, str]] = None,
                                      use_comprehensive: bool = False) -> Dict[str, any]:
        """Send a request and capture both request and response headers.
        
        Args:
            url: The URL to request
            custom_headers: Custom headers to include
            use_comprehensive: Whether to use comprehensive headers
            
        Returns:
            Dictionary containing request/response data and status
        """
        try:
            # Ensure URL has a scheme
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            # Prepare headers
            headers = {}
            if use_comprehensive and not custom_headers:
                headers.update(self.config['comprehensive_headers'])
            if custom_headers:
                headers.update(custom_headers)
            
            # Prepare and send the request
            req = requests.Request('GET', url, headers=headers)
            prepared = self.session.prepare_request(req)
            
            # Send the request
            response = self.session.send(prepared, timeout=self.timeout)
            
            return {
                'url': response.url,
                'status_code': response.status_code,
                'request_headers_sent': dict(prepared.headers),
                'response_headers_received': dict(response.headers),
                'status': 'success'
            }
            
        except requests.RequestException as e:
            response = getattr(e, 'response', None)
            return {
                'url': url,
                'error': str(e),
                'status_code': response.status_code if response else None,
                'request_headers_sent': dict(getattr(e.request, 'headers', {})),
                'response_headers_received': dict(response.headers) if response else {},
                'status': 'error'
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status_code': None,
                'request_headers_sent': {},
                'response_headers_received': {},
                'status': 'error'
            }


def main():
    """Main function to demonstrate the HeaderExtractor usage."""
    
    # Create an instance of HeaderExtractor
    extractor = HeaderExtractor()
    
    # If URLs are provided as command line arguments, use them
    # Otherwise, use example URLs
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        print("No URLs provided. Using example URLs.")
        urls = [
            'https://httpbin.org/headers',
            'https://example.com',
            'https://httpbin.org/user-agent'
        ]
    
    # Extract information from each URL
    for url in urls:
        print(f"\n{'='*60}")
        print(f"Extracting request headers for: {url}")
        print('='*60)
        
        # Extract request headers
        result = extractor.send_request_and_capture_headers(url)
        
        # Pretty print the results
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()