"""
Google Gemini API Client
========================
Wrapper for Google Gemini 2.0 Flash API with error handling and rate limiting.
"""

import requests
from typing import Optional, Dict, Any
from loguru import logger

from ..utils.rate_limiter import RateLimiter
from ..utils.retry import retry_with_backoff


class GeminiError(Exception):
    """Raised when Gemini API returns an error."""
    pass


class GeminiClient:
    """
    Client for Google Gemini 2.0 Flash API.

    Provides text generation capabilities using Google's Gemini model with
    automatic retry logic, rate limiting, and error handling.

    Attributes:
        api_key: Google Gemini API key
        base_url: API endpoint base URL
        model: Model identifier
        rate_limiter: Rate limiter instance for API calls

    Example:
        >>> client = GeminiClient(api_key="your_key")
        >>> response = client.generate_text("What is a perovskite?")
        >>> print(response)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        requests_per_second: float = 0.5
    ):
        """
        Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            model: Model identifier (default: gemini-2.5-flash)
            requests_per_second: Rate limit for API calls (default: 0.5 = 1 per 2 seconds)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.rate_limiter = RateLimiter(calls_per_second=requests_per_second)

        logger.info(f"Initialized GeminiClient with model: {model}")

    def _build_url(self, endpoint: str) -> str:
        """Build full API URL with key parameter."""
        return f"{self.base_url}/{endpoint}?key={self.api_key}"

    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        exceptions=(requests.exceptions.RequestException, GeminiError)
    )
    def generate_text(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini API.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate (None = model default)
            temperature: Sampling temperature (0.0-1.0, higher = more random)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            system_instruction: Optional system instruction for the model

        Returns:
            Generated text as string

        Raises:
            GeminiError: If API returns an error
            requests.exceptions.RequestException: If network error occurs

        Example:
            >>> response = client.generate_text(
            ...     "Explain photosynthesis",
            ...     max_tokens=500,
            ...     temperature=0.3
            ... )
        """
        # Apply rate limiting
        self.rate_limiter.wait()

        # Build request URL
        url = self._build_url(f"models/{self.model}:generateContent")

        # Build request payload
        payload: Dict[str, Any] = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p,
                "topK": top_k,
            }
        }

        # Add optional parameters
        if max_tokens is not None:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Make API request
        logger.debug(f"Sending request to Gemini API: {len(prompt)} chars")

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            error_msg = f"Gemini API HTTP error: {e}"
            if response.text:
                error_msg += f"\nResponse: {response.text}"
            logger.error(error_msg)
            raise GeminiError(error_msg)

        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {e}")
            raise

        # Parse response
        try:
            data = response.json()

            # Check for API-level errors
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                logger.error(f"Gemini API error: {error_msg}")
                raise GeminiError(f"API error: {error_msg}")

            # Extract generated text
            if "candidates" not in data or not data["candidates"]:
                raise GeminiError("No candidates in response")

            candidate = data["candidates"][0]

            # Check for content filtering
            if "content" not in candidate:
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                logger.warning(f"Content filtered or blocked: {finish_reason}")
                raise GeminiError(f"Content blocked: {finish_reason}")

            # Extract text from parts
            parts = candidate["content"]["parts"]
            generated_text = "".join(part.get("text", "") for part in parts)

            logger.info(
                f"Generated {len(generated_text)} characters from Gemini")
            return generated_text

        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            raise GeminiError(f"Response parsing error: {e}")

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text (approximate).

        Args:
            text: Input text

        Returns:
            Estimated token count

        Note:
            This is a rough estimate. Actual tokenization may differ.
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4

    def test_connection(self) -> bool:
        """
        Test if API key is valid and connection works.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate_text(
                "Hello! Please respond with 'OK'.",
                max_tokens=10
            )
            logger.info("Gemini API connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            return False
