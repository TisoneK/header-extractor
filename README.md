# Header Extractor

A simple Python tool to extract HTTP request headers that would be sent to web pages, with full support for comprehensive browser headers.

## Features

- Extract request headers that would be sent to any URL
- Send actual requests and capture both request and response headers
- Handle HTTP errors gracefully
- Support for comprehensive browser headers to bypass anti-bot measures
- Simple API for easy integration
- JSON output for easy parsing

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Simple Usage - Extract Request Headers

```python
from header_extractor import HeaderExtractor

# Create extractor instance
extractor = HeaderExtractor()

# Extract request headers that would be sent
result = extractor.extract_request_headers("https://linebet.com")

# Access the request headers
request_headers = result['request_headers']
for key, value in request_headers.items():
    print(f"{key}: {value}")
```

## Usage with Comprehensive Browser Headers

```python
from header_extractor import HeaderExtractor

# Create extractor instance
extractor = HeaderExtractor()

# Define comprehensive browser headers to bypass anti-bot measures
comprehensive_headers = {
    # Content negotiation headers
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    
    # Cache control (anti-bot detection)
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    
    # Priority headers (modern browser feature)
    'priority': 'u=0, i',
    
    # Client Hints (modern replacement for parts of User-Agent)
    'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    
    # Security/Fetch metadata headers
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    
    # User-Agent (still important for compatibility)
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}

# Extract request headers with comprehensive headers
result = extractor.extract_request_headers("https://linebet.com", comprehensive_headers)

# Print the request headers that would be sent
print("Request Headers That Would Be Sent:")
for key, value in result['request_headers'].items():
    print(f"{key}: {value}")
```

## Send Request and Capture Both Headers

```python
from header_extractor import HeaderExtractor

# Create extractor instance
extractor = HeaderExtractor()

# Send request and capture both request and response headers
result = extractor.send_request_and_capture_headers("https://linebet.com")

# Access both request and response headers
print("Request Headers Sent:")
for key, value in result['request_headers_sent'].items():
    print(f"  {key}: {value}")

print("\nResponse Headers Received:")
for key, value in result['response_headers_received'].items():
    print(f"  {key}: {value}")
```

## Command Line Usage

You can also use the tool from the command line:

```bash
# Basic usage
python -m header_extractor.cli https://example.com

# Multiple URLs
python -m header_extractor.cli https://example.com https://httpbin.org/headers

# Custom timeout
python -m header_extractor.cli https://example.com --timeout 30

# Save to file
python -m header_extractor.cli https://example.com --output headers.json

# Inline format
python -m header_extractor.cli https://example.com --format inline
```

## Why Comprehensive Headers Matter

Many modern websites, especially those with anti-bot measures, analyze these headers to determine if the request is coming from a genuine browser or a script:

- **accept/accept-language**: Content negotiation headers that indicate browser capabilities
- **sec-ch-ua***: Client Hints that provide structured browser information
- **sec-fetch-dest/mode/site**: Security headers that indicate request context
- **upgrade-insecure-requests**: Directive for HTTPS preference
- **cache-control/pragma**: Cache behavior indicators

A request with only basic headers (User-Agent, Accept-Encoding, Connection) looks very "programmatic" to a server and may be blocked by anti-bot systems.

## API Reference

### HeaderExtractor Class

#### Constructor
```python
extractor = HeaderExtractor(timeout=10)
```

Parameters:
- `timeout` (int): Request timeout in seconds (default: 10)

#### Methods

##### extract_request_headers(url, custom_headers=None)
Extract the request headers that would be sent to a given URL.

Parameters:
- `url` (str): The URL to send request to
- `custom_headers` (dict, optional): Custom headers to include in the request

Returns:
- `dict`: A dictionary containing the request headers that would be sent

##### send_request_and_capture_headers(url, custom_headers=None)
Send a request and capture both request and response headers.

Parameters:
- `url` (str): The URL to send request to
- `custom_headers` (dict, optional): Custom headers to include in the request

Returns:
- `dict`: A dictionary containing both request and response headers

## Requirements

- Python 3.6+
- See [requirements.txt](requirements.txt) for Python package dependencies

## License

This project is open source and available under the MIT License.