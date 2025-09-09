"""
Command Line Interface for Header Extractor
"""

import argparse
import json
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

from .main import HeaderExtractor
from .config import get_config, update_config


def format_result(result: Dict[str, Any], fmt: str = 'json') -> str:
    """Format the result based on the specified format.
    
    Args:
        result: The result dictionary to format
        fmt: Output format ('json' or 'inline')
        
    Returns:
        Formatted string representation of the result
    """
    if fmt == 'inline':
        output = []
        if 'error' in result:
            output.append(f"Error for {result['url']}: {result['error']}")
        else:
            output.append(f"URL: {result['url']}")
            if 'status_code' in result:
                output.append(f"Status: {result['status_code']}")
            if 'request_headers' in result:
                output.append("\nRequest Headers:")
                for k, v in result.get('request_headers', {}).items():
                    output.append(f"  {k}: {v}")
            if 'response_headers_received' in result:
                output.append("\nResponse Headers:")
                for k, v in result.get('response_headers_received', {}).items():
                    output.append(f"  {k}: {v}")
        return '\n'.join(output)
    
    # Default to JSON
    return json.dumps(result, indent=2)


def process_urls(extractor: HeaderExtractor, urls: List[str], 
                output_file: Optional[str] = None, 
                output_format: str = 'json') -> None:
    """Process multiple URLs and handle output.
    
    Args:
        extractor: Initialized HeaderExtractor instance
        urls: List of URLs to process
        output_file: Optional file to save results
        output_format: Output format ('json' or 'inline')
    """
    results = []
    
    for url in urls:
        try:
            result = extractor.send_request_and_capture_headers(url)
            results.append(result)
            print(format_result(result, output_format))
            if len(urls) > 1:
                print("\n" + "="*80 + "\n")  # Separator between results
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            break
        except Exception as e:
            print(f"Error processing {url}: {str(e)}", file=sys.stderr)
    
    # Save to file if specified
    if output_file:
        output_path = Path(output_file)
        extractor.save_to_file(results if len(results) != 1 else results[0], 
                             output_path.name, output_path.parent)


def main():
    """Main CLI function."""
    config = get_config()
    
    parser = argparse.ArgumentParser(
        description="Extract HTTP headers from web pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  header-extractor https://example.com
  header-extractor https://example.com https://httpbin.org/headers
  header-extractor https://example.com --timeout 30
  header-extractor https://example.com --output headers.json
  header-extractor https://example.com --format inline
  header-extractor --set-config '{"default_timeout": 20}'
        """
    )
    
    # Main arguments
    parser.add_argument(
        'urls',
        metavar='URL',
        nargs='*',
        help='URL(s) to extract headers from'
    )
    
    # Configuration arguments
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument(
        '--set-config',
        type=json.loads,
        help='Update configuration with a JSON string (e.g., \'{"default_timeout": 20}\')'
    )
    config_group.add_argument(
        '--show-config',
        action='store_true',
        help='Show current configuration and exit'
    )
    
    # Request options
    request_group = parser.add_argument_group('Request Options')
    request_group.add_argument(
        '--timeout',
        type=int,
        default=config['default_timeout'],
        help=f'Request timeout in seconds (default: {config["default_timeout"]})'
    )
    request_group.add_argument(
        '--comprehensive',
        '-c',
        action='store_true',
        help='Use comprehensive set of headers'
    )
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument(
        '--output',
        '-o',
        type=str,
        help=f'Output file (default: {config["output_dir"]}/headers_<timestamp>.json)'
    )
    output_group.add_argument(
        '--format',
        '-f',
        choices=['json', 'inline'],
        default='json',
        help='Output format (default: json)'
    )
    
    output_group.add_argument(
        '--no-request-headers',
        action='store_true',
        help='Do not include request headers in output'
    )
    
    output_group.add_argument(
        '--no-response-headers',
        action='store_true',
        help='Do not include response headers in output'
    )
    
    args = parser.parse_args()
    
    # Handle configuration commands
    if args.set_config:
        update_config(args.set_config)
        print("Configuration updated successfully.")
        print(json.dumps(get_config(), indent=2))
        return
        
    if args.show_config:
        print("Current configuration:")
        print(json.dumps(get_config(), indent=2))
        return
    
    # Check if URLs are provided
    if not args.urls:
        parser.print_help()
        print("\nError: No URLs provided")
        return 1
    
    try:
        # Create extractor with specified timeout and headers
        extractor = HeaderExtractor(
            timeout=args.timeout,
            custom_headers=config['comprehensive_headers'] if args.comprehensive else None
        )
        
        # Process URLs and handle output
        process_urls(
            extractor=extractor,
            urls=args.urls,
            output_file=args.output,
            output_format=args.format
        )
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
        
    return 0


if __name__ == "__main__":
    main()