"""
Sequence-based header extraction system.

This module provides a way to define and execute sequences of HTTP requests
where each step can depend on data from previous steps.
"""

import json
import time
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path

from .main import HeaderExtractor


@dataclass
class StepResult:
    """Result of executing a single step in the sequence."""
    name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    response: Optional[Any] = None
    execution_time: float = 0.0


class SequenceExtractor:
    """
    A class to manage and execute sequences of HTTP requests with dependencies.
    """
    
    def __init__(self, extractor: Optional[HeaderExtractor] = None):
        """
        Initialize the sequence extractor.
        
        Args:
            extractor: Optional HeaderExtractor instance. If not provided,
                     a new one will be created.
        """
        self.extractor = extractor or HeaderExtractor()
        self.steps: List[Dict] = []
        self.results: Dict[str, StepResult] = {}
        self.context: Dict[str, Any] = {}
    
    def add_step(
        self,
        name: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
        condition: Optional[Callable[[Dict], bool]] = None,
        extract: Optional[Dict[str, str]] = None,
        max_retries: int = 1,
        delay: float = 0,
        **kwargs
    ) -> None:
        """
        Add a step to the sequence.
        
        Args:
            name: Unique identifier for this step
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            headers: Headers to include in the request
            data: Request body data
            depends_on: List of step names that must complete successfully first
            condition: Callable that receives context and returns whether to execute
            extract: Dict of {name: json_path} to extract data from response
            max_retries: Maximum number of retry attempts
            delay: Delay in seconds before executing this step
            **kwargs: Additional arguments to pass to the request
        """
        self.steps.append({
            "name": name,
            "url": url,
            "method": method.upper(),
            "headers": headers or {},
            "data": data,
            "depends_on": depends_on or [],
            "condition": condition,
            "extract": extract or {},
            "max_retries": max_retries,
            "delay": delay,
            **kwargs
        })
    
    def _evaluate_condition(self, condition: Callable[[Dict], bool], context: Dict) -> bool:
        """Safely evaluate a condition function."""
        try:
            return condition(context)
        except Exception:
            return False
    
    def _extract_data(self, response: Any, extract_rules: Dict[str, str]) -> Dict[str, Any]:
        """Extract data from response according to rules."""
        extracted = {}
        try:
            data = response.json() if hasattr(response, 'json') else response.text

            def _get_by_dot_path(obj: Any, dot_path: str) -> Any:
                # Supports simple dot-separated traversal for dicts
                if not isinstance(obj, dict):
                    return None
                current = obj
                for part in dot_path.split('.'):
                    if not isinstance(current, dict):
                        return None
                    # exact key match first
                    if part in current:
                        current = current[part]
                        continue
                    # try case-insensitive match as fallback
                    lowered = {str(k).lower(): k for k in current.keys()}
                    lk = part.lower()
                    if lk in lowered:
                        current = current[lowered[lk]]
                    else:
                        return None
                return current

            for key, path in extract_rules.items():
                if isinstance(data, dict):
                    # dot-path or direct key
                    value = _get_by_dot_path(data, path) if '.' in path else data.get(path)
                    if value is not None:
                        extracted[key] = value
                # no elif for text; only JSON extraction supported for now
                    
        except Exception as e:
            pass  # Silently fail extraction
            
        return extracted
    
    def execute_step(self, step: Dict) -> StepResult:
        """Execute a single step in the sequence."""
        step_name = step["name"]
        result = StepResult(name=step_name, success=False)
        start_time = time.time()
        
        try:
            # Check dependencies
            for dep in step["depends_on"]:
                if dep not in self.results or not self.results[dep].success:
                    raise Exception(f"Dependency {dep} failed or not executed")
            
            # Check condition
            if step["condition"] and not self._evaluate_condition(step["condition"], self.context):
                result.success = True
                result.data["skipped"] = True
                result.execution_time = time.time() - start_time
                return result
            
            # Apply delay if specified
            if step["delay"] > 0:
                time.sleep(step["delay"])
            
            # Prepare request
            url = step["url"].format(**self.context)
            
            # Handle callable headers and data
            headers = step.get("headers", {})
            
            # Process headers - handle callables and string formatting
            processed_headers = {}
            if callable(headers):
                headers = headers(self.context) or {}
            
            for k, v in headers.items():
                if callable(v):
                    # If the value is a callable, call it with the context
                    processed_headers[k] = v(self.context)
                elif isinstance(v, str):
                    # If it's a string, try to format it with context
                    try:
                        processed_headers[k] = v.format(**self.context)
                    except (KeyError, ValueError):
                        processed_headers[k] = v
                else:
                    processed_headers[k] = v
            
            # Ensure required headers are present
            if 'User-Agent' not in processed_headers:
                processed_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            if 'Accept' not in processed_headers:
                processed_headers['Accept'] = 'application/json, text/plain, */*'
            
            # Get request params and data with callable + formatting support
            params = step.get("params")
            if callable(params):
                params = params(self.context)
            elif isinstance(params, dict):
                formatted_params = {}
                for pk, pv in params.items():
                    if callable(pv):
                        formatted_params[pk] = pv(self.context)
                    elif isinstance(pv, str):
                        try:
                            formatted_params[pk] = pv.format(**self.context)
                        except (KeyError, ValueError):
                            formatted_params[pk] = pv
                    else:
                        formatted_params[pk] = pv
                params = formatted_params

            data = step.get("data")
            if callable(data):
                data = data(self.context)
            elif isinstance(data, dict):
                formatted_data = {}
                for dk, dv in data.items():
                    if callable(dv):
                        formatted_data[dk] = dv(self.context)
                    elif isinstance(dv, str):
                        try:
                            formatted_data[dk] = dv.format(**self.context)
                        except (KeyError, ValueError):
                            formatted_data[dk] = dv
                    else:
                        formatted_data[dk] = dv
                data = formatted_data
            
            # Execute request with retries
            for attempt in range(step["max_retries"] + 1):
                try:
                    request_kwargs = {
                        'url': url,
                        'headers': processed_headers,
                        'timeout': self.extractor.timeout
                    }
                    
                    if step["method"] == "GET":
                        request_kwargs['params'] = params
                        response = self.extractor.session.get(**request_kwargs)
                    elif step["method"] == "POST":
                        request_kwargs['json'] = data
                        response = self.extractor.session.post(**request_kwargs)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {step['method']}")
                    
                    response.raise_for_status()
                    break
                except Exception as e:
                    if attempt == step["max_retries"]:
                        raise
                    time.sleep(1)  # Wait before retry
            
            # Extract data if needed
            if step["extract"]:
                extracted = self._extract_data(response, step["extract"])
                self.context.update(extracted)
                result.data.update(extracted)
            
            result.success = True
            result.response = response
            self.context[f"{step_name}_response"] = response
            
        except Exception as e:
            result.error = str(e)
            result.success = False
        
        result.execution_time = time.time() - start_time
        return result
    
    def execute(self) -> Dict[str, StepResult]:
        """Execute all steps in the sequence."""
        self.results = {}
        
        for step in self.steps:
            if step["name"] in self.results:
                continue  # Skip already executed steps
                
            result = self.execute_step(step)
            self.results[step["name"]] = result
            
            if not result.success and not step.get("continue_on_failure", False):
                break  # Stop on failure unless continue_on_failure is True
        
        return self.results
    
    def save_sequence(self, filepath: Union[str, Path]) -> None:
        """Save the sequence definition to a file."""
        def _serialize_step(step: Dict[str, Any]) -> Dict[str, Any]:
            # Remove or stringify non-serializable callables
            serializable = {}
            for k, v in step.items():
                if callable(v):
                    # store a hint for debugging but avoid trying to reload functions
                    serializable[k] = f"<callable:{getattr(v, '__name__', 'anonymous')}>"
                elif isinstance(v, dict):
                    # shallow process for nested dicts possibly containing callables
                    nested = {}
                    for nk, nv in v.items():
                        nested[nk] = f"<callable:{getattr(nv, '__name__', 'anonymous')}>" if callable(nv) else nv
                    serializable[k] = nested
                else:
                    serializable[k] = v
            return serializable

        serializable_steps = [_serialize_step(s) for s in self.steps]
        with open(filepath, 'w') as f:
            json.dump(serializable_steps, f, indent=2)
    
    @classmethod
    def load_sequence(cls, filepath: Union[str, Path], extractor: Optional[HeaderExtractor] = None) -> 'SequenceExtractor':
        """Load a sequence definition from a file."""
        with open(filepath, 'r') as f:
            steps = json.load(f)
        
        seq = cls(extractor)
        seq.steps = steps
        return seq


def main():
    """Example usage of the SequenceExtractor."""
    # Create a sequence
    seq = SequenceExtractor()
    
    # Add steps
    seq.add_step(
        name="get_homepage",
        url="https://httpbin.org/headers",
        headers={"User-Agent": "SequenceExtractor/1.0"},
        extract={"user_agent": "User-Agent"}
    )
    
    seq.add_step(
        name="get_user_agent",
        url="https://httpbin.org/user-agent",
        depends_on=["get_homepage"],
        extract={"server_ua": "user-agent"}
    )
    
    # Execute the sequence
    results = seq.execute()
    
    # Print results
    for name, result in results.items():
        print(f"Step: {name}")
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")
        if result.data:
            print("Extracted data:", result.data)
        print()


if __name__ == "__main__":
    main()
