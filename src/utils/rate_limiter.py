"""
Rate limiter for API calls
"""
import time
import threading
from typing import Optional
from collections import deque


class RateLimiter:
    """
    Token bucket rate limiter for API calls

    Attributes:
        calls_per_minute: Maximum number of calls allowed per minute
        calls_per_second: Maximum number of calls allowed per second
    """

    def __init__(
        self,
        calls_per_minute: int = 60,
        calls_per_second: Optional[int] = None
    ):
        """
        Initialize rate limiter

        Args:
            calls_per_minute: Maximum calls per minute
            calls_per_second: Maximum calls per second (optional)
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_second = calls_per_second
        self._minute_window = deque()
        self._second_window = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        """
        Acquire permission to make an API call
        Blocks until call is allowed within rate limits
        """
        with self._lock:
            current_time = time.time()

            # Clean up old entries from minute window
            while self._minute_window and current_time - self._minute_window[0] >= 60:
                self._minute_window.popleft()

            # Clean up old entries from second window
            while self._second_window and current_time - self._second_window[0] >= 1:
                self._second_window.popleft()

            # Check if we need to wait for minute limit
            if len(self._minute_window) >= self.calls_per_minute:
                wait_time = 60 - (current_time - self._minute_window[0])
                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time = time.time()
                    self._minute_window.popleft()

            # Check if we need to wait for second limit
            if self.calls_per_second and len(self._second_window) >= self.calls_per_second:
                wait_time = 1 - (current_time - self._second_window[0])
                if wait_time > 0:
                    time.sleep(wait_time)
                    current_time = time.time()
                    self._second_window.popleft()

            # Add current call to windows
            self._minute_window.append(current_time)
            if self.calls_per_second:
                self._second_window.append(current_time)

    def wait_if_needed(self) -> None:
        """
        Alias for acquire() for backward compatibility
        """
        self.acquire()

    def wait(self) -> None:
        """
        Another alias for acquire() for backward compatibility
        """
        self.acquire()

    def __enter__(self):
        """Context manager entry"""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass
