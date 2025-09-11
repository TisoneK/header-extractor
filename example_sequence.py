"""
Example usage of the SequenceExtractor class with httpbin.org test endpoints.
"""
from header_extractor.sequence_extractor import SequenceExtractor
from header_extractor.main import HeaderExtractor

def run_example_sequence():
    # Create a header extractor with custom settings
    extractor = HeaderExtractor(timeout=10)
    
    # Create a sequence
    seq = SequenceExtractor(extractor)
    
    # Step 1: Get initial data
    seq.add_step(
        name="get_initial_data",
        url="https://httpbin.org/get",
        extract={"origin_ip": "origin"}
    )
    
    # Step 2: Send data (depends on first step)
    seq.add_step(
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
    
    # Step 3: Get headers (depends on previous step)
    seq.add_step(
        name="get_headers",
        url="https://httpbin.org/headers",
        depends_on=["post_data"],
        headers=lambda ctx: {
            "X-Client-IP": ctx.get("origin_ip", ""),
            "User-Agent": "SequenceExtractor/1.0"
        }
    )
    
    # Execute the sequence
    results = seq.execute()
    
    # Print results
    for name, result in results.items():
        print(f"\n{'='*50}")
        print(f"Step: {name}")
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")
        if result.data:
            print("\nExtracted data:")
            for k, v in result.data.items():
                print(f"  {k}: {v}")
        print(f"Time: {result.execution_time:.2f}s")
    
    return results


if __name__ == "__main__":
    run_example_sequence()
