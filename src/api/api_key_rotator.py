"""
API Key Rotation Manager
Handles multiple API keys per service, auto-rotates on rate limits
"""

import os
import time
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from ..utils.logger import setup_logger

logger = setup_logger()


@dataclass
class APIKeyStatus:
    """Track status of a single API key"""
    key: str
    service: str
    request_count: int = 0
    last_used: Optional[datetime] = None
    rate_limited_until: Optional[datetime] = None
    is_active: bool = True
    error_count: int = 0


class APIKeyRotator:
    """
    Manages multiple API keys for a service with automatic rotation
    """

    def __init__(self, service_name: str, keys: List[str]):
        """
        Initialize key rotator

        Args:
            service_name: Name of service (gemini, groq, materials_project)
            keys: List of API keys to rotate through
        """
        self.service_name = service_name
        self.keys = [APIKeyStatus(key=k, service=service_name)
                     for k in keys if k]
        self.current_index = 0

        if not self.keys:
            raise ValueError(f"No valid API keys provided for {service_name}")

        logger.info(
            f"Initialized {service_name} with {len(self.keys)} API keys")

    def get_current_key(self) -> str:
        """
        Get current active API key

        Returns:
            API key string
        """
        # Skip rate-limited keys
        attempts = 0
        while attempts < len(self.keys):
            key_status = self.keys[self.current_index]

            # Check if rate limit expired
            if key_status.rate_limited_until:
                if datetime.now() > key_status.rate_limited_until:
                    key_status.rate_limited_until = None
                    key_status.is_active = True
                    logger.info(
                        f"{self.service_name} key {self.current_index + 1} rate limit expired, reactivating")

            # Return if key is active
            if key_status.is_active and not key_status.rate_limited_until:
                key_status.last_used = datetime.now()
                key_status.request_count += 1
                return key_status.key

            # Try next key
            self.rotate()
            attempts += 1

        # All keys exhausted
        raise Exception(
            f"All {self.service_name} API keys are rate-limited or inactive")

    def rotate(self) -> None:
        """Rotate to next API key"""
        self.current_index = (self.current_index + 1) % len(self.keys)
        logger.debug(
            f"Rotated to {self.service_name} key {self.current_index + 1}/{len(self.keys)}")

    def mark_rate_limited(self, duration_minutes: int = 60) -> None:
        """
        Mark current key as rate-limited

        Args:
            duration_minutes: How long to wait before retrying this key
        """
        key_status = self.keys[self.current_index]
        key_status.rate_limited_until = datetime.now() + timedelta(minutes=duration_minutes)
        key_status.is_active = False

        logger.warning(
            f"{self.service_name} key {self.current_index + 1} rate-limited, "
            f"waiting {duration_minutes} minutes"
        )

        # Auto-rotate to next key
        self.rotate()

    def mark_error(self) -> None:
        """Mark current key as having an error"""
        key_status = self.keys[self.current_index]
        key_status.error_count += 1

        # Deactivate after 3 consecutive errors
        if key_status.error_count >= 3:
            key_status.is_active = False
            logger.error(
                f"{self.service_name} key {self.current_index + 1} deactivated after 3 errors")
            self.rotate()

    def reset_error_count(self) -> None:
        """Reset error count on successful request"""
        self.keys[self.current_index].error_count = 0

    def get_status(self) -> Dict:
        """Get status of all keys"""
        return {
            'service': self.service_name,
            'total_keys': len(self.keys),
            'active_keys': sum(1 for k in self.keys if k.is_active),
            'current_index': self.current_index,
            'keys': [
                {
                    'index': i + 1,
                    'active': k.is_active,
                    'requests': k.request_count,
                    'errors': k.error_count,
                    'rate_limited': k.rate_limited_until is not None
                }
                for i, k in enumerate(self.keys)
            ]
        }

    @staticmethod
    def load_from_env(service_name: str) -> 'APIKeyRotator':
        """
        Load API keys from environment variables

        Expected format:
            GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3
            GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3
            MP_API_KEY_1, MP_API_KEY_2, MP_API_KEY_3

        Args:
            service_name: gemini, groq, or materials_project

        Returns:
            APIKeyRotator instance
        """
        key_mapping = {
            'gemini': 'GEMINI_API_KEY',
            'groq': 'GROQ_API_KEY',
            'materials_project': 'MP_API_KEY'
        }

        env_prefix = key_mapping.get(service_name.lower())
        if not env_prefix:
            raise ValueError(f"Unknown service: {service_name}")

        # Try to load up to 3 keys
        keys = []
        for i in range(1, 4):
            key = os.getenv(f"{env_prefix}_{i}")
            if key and key.strip() and not key.startswith('your_'):
                keys.append(key)

        # Fallback to single key (backward compatibility)
        if not keys:
            key = os.getenv(env_prefix)
            if key and key.strip() and not key.startswith('your_'):
                keys.append(key)

        if not keys:
            raise ValueError(f"No API keys found for {service_name}")

        return APIKeyRotator(service_name, keys)


# Decorator for automatic retry with key rotation
def with_key_rotation(rotator: APIKeyRotator, max_retries: int = 3):
    """
    Decorator to automatically handle rate limits with key rotation

    Usage:
        @with_key_rotation(gemini_rotator, max_retries=3)
        def api_call(api_key, ...):
            # Make API call
            pass
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    # Get current key
                    api_key = rotator.get_current_key()

                    # Inject key as first argument or kwarg
                    if 'api_key' in kwargs:
                        kwargs['api_key'] = api_key
                    else:
                        args = (api_key,) + args

                    # Make API call
                    result = func(*args, **kwargs)

                    # Success - reset error count
                    rotator.reset_error_count()
                    return result

                except Exception as e:
                    error_str = str(e).lower()

                    # Check if rate limit error
                    if '429' in error_str or 'rate limit' in error_str or 'quota' in error_str:
                        logger.warning(
                            f"Rate limit hit on attempt {attempt + 1}")
                        rotator.mark_rate_limited(duration_minutes=60)

                        if attempt < max_retries - 1:
                            time.sleep(2)  # Brief pause before retry
                            continue

                    # Other error
                    rotator.mark_error()

                    if attempt < max_retries - 1:
                        time.sleep(1)
                        continue
                    else:
                        raise

            raise Exception(f"All retries failed for {rotator.service_name}")

        return wrapper
    return decorator
