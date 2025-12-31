"""
Helper Utilities for Autonomous Scientific Agent
================================================
Common functions for retry logic, rate limiting, file I/O, and more.
"""

import time
import json
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar
from functools import wraps
from loguru import logger

T = TypeVar('T')


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function with retry logic

    Example:
        >>> @retry_with_backoff(max_retries=3, initial_delay=1.0)
        ... def fetch_data():
        ...     # Code that might fail
        ...     return api.get("/data")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"{func.__name__} failed after {max_retries} retries: {e}"
                        )

            # If we get here, all retries failed
            raise last_exception

        return wrapper
    return decorator


class RateLimiter:
    """
    Rate limiter to control API request frequency.

    Ensures a minimum time gap between consecutive calls.

    Attributes:
        min_interval: Minimum seconds between calls
        last_call_time: Timestamp of last call

    Example:
        >>> limiter = RateLimiter(calls_per_second=2)
        >>> limiter.wait()  # Blocks if called too soon
        >>> make_api_call()
    """

    def __init__(self, calls_per_second: float = 1.0):
        """
        Initialize rate limiter.

        Args:
            calls_per_second: Maximum number of calls allowed per second
        """
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time: Optional[float] = None

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        if self.last_call_time is not None:
            elapsed = time.time() - self.last_call_time
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)

        self.last_call_time = time.time()


def rate_limiter(calls_per_second: float = 1.0) -> Callable:
    """
    Decorator that applies rate limiting to a function.

    Args:
        calls_per_second: Maximum calls allowed per second

    Returns:
        Decorated function with rate limiting

    Example:
        >>> @rate_limiter(calls_per_second=2)
        ... def api_call():
        ...     return requests.get("https://api.example.com")
    """
    limiter = RateLimiter(calls_per_second)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def save_json(data: Any, file_path: str | Path, indent: int = 2) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to save (must be JSON-serializable)
        file_path: Path to output file
        indent: Indentation level for pretty printing

    Example:
        >>> save_json({"result": [1, 2, 3]}, "output.json")
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

    logger.debug(f"Saved JSON to {file_path}")


def load_json(file_path: str | Path, default: Optional[Any] = None) -> Any:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to input file
        default: Default value if file doesn't exist or can't be parsed

    Returns:
        Loaded data or default value

    Example:
        >>> data = load_json("input.json", default={})
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.debug(f"File not found: {file_path}, returning default")
        return default

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.debug(f"Loaded JSON from {file_path}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {file_path}: {e}")
        return default


def format_bytes(size: int) -> str:
    """
    Format byte size as human-readable string.

    Args:
        size: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "3.2 KB")

    Example:
        >>> format_bytes(1536)
        '1.5 KB'
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length (including suffix)
        suffix: String to append if truncated

    Returns:
        Truncated text

    Example:
        >>> truncate_text("This is a very long text", max_length=15)
        'This is a ve...'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
