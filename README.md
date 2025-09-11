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
result = extractor.extract_request_headers("https://example.com")

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
result = extractor.extract_request_headers("https://example.com", comprehensive_headers)

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
result = extractor.send_request_and_capture_headers("https://example.com")

# Access both request and response headers
print("Request Headers Sent:")
for key, value in result['request_headers_sent'].items():
    print(f"  {key}: {value}")

print("\nResponse Headers Received:")
for key, value in result['response_headers_received'].items():
    print(f"  {key}: {value}")
```

## Command Line Usage

You can also use the tool from the command line (after installation, via the `header-extractor` entrypoint):

```bash
# Basic usage
header-extractor https://example.com

# Specify custom output directory
header-extractor https://example.com --output-dir data/headers

# Multiple URLs
header-extractor https://example.com https://httpbin.org/headers

# Custom timeout
header-extractor https://example.com --timeout 30

# Save to file
header-extractor https://example.com --output headers.json

# Inline format
header-extractor https://example.com --format inline
```

## Why Comprehensive Headers Matter

Many modern websites, especially those with anti-bot measures, analyze these headers to determine if the request is coming from a genuine browser or a script:

- **accept/accept-language**: Content negotiation headers that indicate browser capabilities
- **sec-ch-ua***: Client Hints that provide structured browser information
- **sec-fetch-dest/mode/site**: Security headers that indicate request context
- **upgrade-insecure-requests**: Directive for HTTPS preference
- **cache-control/pragma**: Cache behavior indicators

A request with only basic headers (User-Agent, Accept-Encoding, Connection) looks very "programmatic" to a server and may be blocked by anti-bot systems.

## Sequence-Based Header Extraction

The `SequenceExtractor` class allows you to define and execute sequences of HTTP requests where each step can depend on data from previous steps.

### Basic Example

```python
from header_extractor.sequence_extractor import SequenceExtractor

# Create a sequence
executor = SequenceExtractor()

# Step 1: Get initial data
executor.add_step(
    name="get_initial_data",
    url="https://httpbin.org/get",
    extract={"origin_ip": "origin"}  # Extract IP from response
)

# Step 2: Send data (depends on first step)
executor.add_step(
    name="post_data",
    method="POST",
    url="https://httpbin.org/post",
    depends_on=["get_initial_data"],
    data=lambda ctx: {
        "client_ip": ctx.get("origin_ip", ""),
        "action": "test"
    },
    extract={"json_data": "json"}
)

# Step 3: Get headers with custom headers (depends on previous step)
executor.add_step(
    name="get_headers",
    url="https://httpbin.org/headers",
    depends_on=["post_data"],
    headers=lambda ctx: {
        "X-Client-IP": ctx.get("origin_ip", ""),
        "User-Agent": "SequenceExtractor/1.0"
    }
)

# Execute the sequence
results = executor.execute()

# Print results
for name, result in results.items():
    print(f"\nStep: {name}")
    print(f"Success: {result.success}")
    if result.error:
        print(f"Error: {result.error}")
    if result.data:
        print("Extracted data:", result.data)
```

### Key Features

1. **Step Dependencies**: Steps can depend on the successful completion of previous steps
2. **Data Extraction**: Extract data from responses and use it in subsequent requests
3. **Conditional Execution**: Skip steps based on conditions
4. **Retry Logic**: Automatic retries for failed requests
5. **Context Management**: Share data between steps using a context dictionary
6. **Error Handling**: Graceful handling of failures with detailed error information

### Step Configuration

Each step can be configured with the following parameters:

- `name`: Unique identifier for the step
- `url`: The URL to request
- `method`: HTTP method (default: "GET")
- `headers`: Headers to include in the request (can be a dict or callable)
- `data`: Request body data (can be a dict or callable)
- `depends_on`: List of step names that must complete successfully first
- `condition`: Callable that receives context and returns whether to execute
- `extract`: Dict of {name: path} to extract data from response
- `max_retries`: Maximum number of retry attempts (default: 1)
- `delay`: Delay in seconds before executing this step (default: 0)

## API Reference

### HeaderExtractor Class

#### Constructor
```python
extractor = HeaderExtractor(timeout=10, custom_headers=None, output_dir=None)
```

Parameters:
- `timeout` (int): Request timeout in seconds (default: 10)
- `custom_headers` (dict, optional): Custom headers to include in all requests
- `output_dir` (str or Path, optional): Custom output directory for saved files. Uses value from config if not specified.

#### Methods

##### extract_request_headers(url, custom_headers=None)
Extract the request headers that would be sent to a given URL.

Parameters:
- `url` (str): The URL to send request to
- `custom_headers` (dict, optional): Custom headers to include in the request

Returns:
- `dict`: A dictionary containing the request headers that would be sent

##### set_output_dir(output_dir)
Set a new default output directory for saving files.

Parameters:
- `output_dir` (str or Path): New output directory path

Example:
```python
extractor = HeaderExtractor()
extractor.set_output_dir('data/headers')  # All future saves will go here
```

##### save_to_file(data, filename=None, output_dir=None)
Save data to a JSON file in the output directory.

Parameters:
- `data` (dict): Data to save as JSON
- `filename` (str, optional): Output filename. If None, generates a name in format 'headers_<domain>_<date>.json'
- `output_dir` (str or Path, optional): Output directory for this save only. Uses instance output_dir if None.

Returns:
- `str`: Path to the saved file

Example:
```python
# Basic usage
extractor = HeaderExtractor()
extractor.save_to_file(data)  # Saves to default output_dir

# Custom output directory for this save only
extractor.save_to_file(data, output_dir='temp/output')

# Change default output directory for all future saves
extractor.set_output_dir('data/headers')
extractor.save_to_file(data)  # Saves to data/headers/
```

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