"""
Example: Using SequenceExtractor to run dependent HTTP requests and share data.

Run:
    python examples/sequence_extractor_example.py
"""

from header_extractor.sequence_extractor import SequenceExtractor


def main() -> None:
    # Create a sequence executor
    executor = SequenceExtractor()

    # Step 1: GET request and extract client IP from JSON response
    executor.add_step(
        name="get_initial_data",
        url="https://httpbin.org/get",
        extract={
            # httpbin returns { ..., "origin": "x.x.x.x" }
            "origin_ip": "origin",
        },
    )

    # Step 2: POST data using the extracted IP
    executor.add_step(
        name="post_data",
        method="POST",
        url="https://httpbin.org/post",
        depends_on=["get_initial_data"],
        data=lambda ctx: {
            "client_ip": ctx.get("origin_ip", ""),
            "action": "test",
        },
        extract={
            # Extract nested JSON using dot-path support
            "posted_client_ip": "json.client_ip",
        },
    )

    # Step 3: GET headers with dynamic/custom headers leveraging context
    executor.add_step(
        name="get_headers",
        url="https://httpbin.org/headers",
        depends_on=["post_data"],
        headers=lambda ctx: {
            "X-Client-IP": ctx.get("origin_ip", ""),
            "User-Agent": "SequenceExtractor/1.0",
        },
        extract={
            # httpbin nests headers under the 'headers' key
            "reflected_client_ip": "headers.X-Client-IP",
            "reflected_user_agent": "headers.User-Agent",
        },
    )

    # Execute the sequence
    results = executor.execute()

    # Print results
    for name, result in results.items():
        print(f"\nStep: {name}")
        print(f"Success: {result.success}")
        print(f"Execution time: {result.execution_time:.3f}s")
        if result.error:
            print(f"Error: {result.error}")
        if result.data:
            print("Extracted data:", result.data)


if __name__ == "__main__":
    main()


