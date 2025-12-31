"""
Hugging Face API Client
=======================
Wrapper for Hugging Face Inference Providers API with chat completions support.
"""

import requests
import time
from typing import Optional, Dict, Any, List
from loguru import logger

from ..utils.rate_limiter import RateLimiter
from ..utils.retry import retry_with_backoff


class HuggingFaceError(Exception):
    """Raised when Hugging Face API returns an error."""
    pass


class HuggingFaceClient:
    """
    Client for Hugging Face Inference Providers API.

    Uses the modern router endpoint with OpenAI-compatible chat completions.
    Provides access to provider-backed instruction models for text generation.

    Attributes:
        token: Hugging Face API token
        base_url: API router endpoint URL
        rate_limiter: Rate limiter instance for API calls

    Example:
        >>> client = HuggingFaceClient(token="your_token")
        >>> response = client.generate_text(
        ...     "Explain quantum mechanics",
        ...     model="mistralai/Mistral-7B-Instruct-v0.2"
        ... )
    """

    def __init__(
        self,
        token: str,
        requests_per_second: float = 1.0
    ):
        """
        Initialize Hugging Face client.

        Args:
            token: Hugging Face API token
            requests_per_second: Rate limit for API calls (default: 1.0)
        """
        self.token = token
        # Use OpenAI-compatible chat completions endpoint
        self.base_url = "https://router.huggingface.co/v1/chat/completions"
        self.rate_limiter = RateLimiter(calls_per_second=requests_per_second)

        logger.info(
            "Initialized HuggingFaceClient with Router Chat Completions API")

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @retry_with_backoff(
        max_retries=3,
        initial_delay=5.0,
        backoff_factor=1.5,
        exceptions=(requests.exceptions.RequestException, HuggingFaceError)
    )
    def generate_text(
        self,
        prompt: str,
        model: str = "mistralai/Mistral-7B-Instruct-v0.2",
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.95,
        system_message: Optional[str] = None
    ) -> str:
        """
        Generate text using Hugging Face Router with OpenAI-compatible chat completions.

        Args:
            prompt: Input text prompt
            model: Model identifier (e.g., "google/flan-t5-small")
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling threshold
            system_message: Optional system message for context

        Returns:
            Generated text as string

        Raises:
            HuggingFaceError: If API returns an error
            requests.exceptions.RequestException: If network error occurs

        Example:
            >>> response = client.generate_text(
            ...     "What is machine learning?",
            ...     model="google/flan-t5-small",
            ...     max_tokens=300
            ... )
        """
        # Apply rate limiting
        self.rate_limiter.wait()

        # Build messages array (OpenAI-compatible format)
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        # Build request payload (OpenAI-compatible)
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }

        # Make API request to chat completions endpoint
        logger.debug(f"Sending chat completion request to HF router: {model}")

        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            error_msg = f"HuggingFace API HTTP error: {e}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f"\nError: {error_data.get('error', error_data.get('message', response.text))}"
                except:
                    error_msg += f"\nResponse: {response.text[:500]}"
            logger.error(error_msg)
            raise HuggingFaceError(error_msg)

        except requests.exceptions.RequestException as e:
            logger.error(f"HuggingFace API request failed: {e}")
            raise

        # Parse OpenAI-compatible response
        try:
            data = response.json()

            # Extract from OpenAI-style response format
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    generated_text = choice["message"]["content"]
                else:
                    raise HuggingFaceError(
                        "Missing content in response message")
            else:
                raise HuggingFaceError("No choices in response")

            logger.info(
                f"Generated {len(generated_text)} characters from HF router")
            return generated_text

        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Failed to parse HuggingFace response: {e}")
            raise HuggingFaceError(f"Response parsing error: {e}")
            raise HuggingFaceError(f"Response parsing error: {e}")

    def get_embeddings(
        self,
        text: str,
        model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> List[float]:
        """
        Generate embeddings for text using a sentence transformer model.

        Note: This uses the legacy inference API endpoint, not the router.
        Embeddings are not yet available via the chat completions endpoint.

        Args:
            text: Input text
            model: Embedding model identifier

        Returns:
            List of embedding values (floats)

        Example:
            >>> embeddings = client.get_embeddings(
            ...     "Machine learning is fascinating",
            ...     model="sentence-transformers/all-MiniLM-L6-v2"
            ... )
            >>> len(embeddings)  # Typically 384 for this model
            384
        """
        # Apply rate limiting
        self.rate_limiter.wait()

        # Use legacy endpoint for embeddings
        url = f"https://api-inference.huggingface.co/models/{model}"
        payload = {
            "inputs": text,
            "options": {"wait_for_model": True}
        }

        logger.debug(f"Getting embeddings from {model}")

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=60
            )
            response.raise_for_status()

            embeddings = response.json()

            # Handle different response formats
            if isinstance(embeddings, list) and len(embeddings) > 0:
                if isinstance(embeddings[0], list):
                    embeddings = embeddings[0]

            logger.info(f"Generated {len(embeddings)}-dimensional embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to get embeddings: {e}")
            raise HuggingFaceError(f"Embeddings error: {e}")

    def test_connection(self) -> bool:
        """
        Test if API token is valid and connection works.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Use a free-tier chat model for testing
            response = self.generate_text(
                "Say hello!",
                model="mistralai/Mistral-7B-Instruct-v0.2",
                max_tokens=20
            )
            logger.info("HuggingFace API connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"HuggingFace API connection test failed: {e}")
            return False
