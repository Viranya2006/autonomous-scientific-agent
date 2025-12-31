"""
GROQ API Client for ultra-fast LLM inference.

This client provides fast, reliable access to GROQ's LLM API using
Llama 3.1 8B Instant model for quick entity extraction and text analysis.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
import requests
from loguru import logger

from ..config.settings import Settings
from ..utils.rate_limiter import RateLimiter
from ..utils.retry import retry_with_backoff


class GROQClient:
    """Client for interacting with GROQ API for fast LLM inference."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.1-8b-instant",
        rate_limit: float = 10.0  # GROQ allows 10 req/s on free tier
    ):
        """
        Initialize GROQ client.

        Args:
            api_key: GROQ API key (uses Settings if not provided)
            model: Model to use (default: llama-3.1-8b-instant)
            rate_limit: Maximum requests per second
        """
        self.api_key = api_key or Settings().groq_api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit)

        logger.info(f"Initialized GROQ client with model: {model}")

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using GROQ API with ultra-fast inference.

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            system_prompt: Optional system prompt

        Returns:
            Generated text response

        Raises:
            requests.HTTPError: If API request fails
        """
        self.rate_limiter.wait_if_needed()

        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        start_time = time.time()

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            elapsed = time.time() - start_time
            result = response.json()

            text = result["choices"][0]["message"]["content"]

            logger.debug(
                f"GROQ generated {len(text)} chars in {elapsed:.2f}s "
                f"(tokens: {result['usage']['total_tokens']})"
            )

            return text

        except requests.exceptions.RequestException as e:
            logger.error(f"GROQ API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def extract_entities(
        self,
        text: str,
        entity_types: List[str] = None,
        max_tokens: int = 1000
    ) -> Dict[str, List[str]]:
        """
        Extract structured entities from text using GROQ's fast inference.

        Args:
            text: Text to analyze
            entity_types: Types of entities to extract
            max_tokens: Maximum tokens for response

        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        if entity_types is None:
            entity_types = [
                "materials",
                "properties",
                "methods",
                "applications",
                "performance_metrics"
            ]

        system_prompt = (
            "You are a scientific entity extraction system. "
            "Extract relevant entities from scientific text and return them "
            "as a JSON object. Be precise and comprehensive."
        )

        prompt = f"""Extract the following entity types from this scientific text:
{', '.join(entity_types)}

Text:
{text[:3000]}  # Limit input length

Return a JSON object with entity types as keys and lists of extracted entities as values.
Example format:
{{
    "materials": ["graphene", "silicon"],
    "properties": ["thermal conductivity", "band gap"],
    "methods": ["DFT calculations", "synthesis"]
}}

Only include entity types that have at least one match. Be specific and avoid duplicates.
"""

        try:
            response = self.generate_text(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.1,  # Low temp for structured extraction
                system_prompt=system_prompt
            )

            # Try to parse JSON from response
            # Handle cases where model adds markdown formatting
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            entities = json.loads(response)

            # Validate structure
            if not isinstance(entities, dict):
                logger.warning("GROQ returned non-dict entities, wrapping")
                entities = {"extracted": [response]}

            logger.info(
                f"Extracted {sum(len(v) for v in entities.values())} entities")
            return entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GROQ JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            # Return empty dict on parse failure
            return {et: [] for et in entity_types}
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {et: [] for et in entity_types}

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def summarize_text(
        self,
        text: str,
        max_summary_length: int = 200,
        focus: Optional[str] = None
    ) -> str:
        """
        Generate concise summary of text.

        Args:
            text: Text to summarize
            max_summary_length: Target summary length in words
            focus: Optional focus area (e.g., "materials", "methods")

        Returns:
            Summary text
        """
        focus_instruction = f" Focus on {focus}." if focus else ""

        prompt = f"""Summarize the following scientific text in approximately {max_summary_length} words.{focus_instruction}

Text:
{text[:4000]}

Provide a clear, concise summary that captures the key findings and implications.
"""

        return self.generate_text(
            prompt=prompt,
            max_tokens=max_summary_length * 2,  # Tokens ~= words * 1.5
            temperature=0.5
        )

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    def classify_text(
        self,
        text: str,
        categories: List[str],
        multi_label: bool = False
    ) -> Dict[str, Any]:
        """
        Classify text into predefined categories.

        Args:
            text: Text to classify
            categories: List of category options
            multi_label: Allow multiple categories if True

        Returns:
            Dictionary with 'categories' (list) and 'confidence' (optional)
        """
        mode = "multiple categories" if multi_label else "single best category"

        prompt = f"""Classify the following scientific text into {mode} from these options:
{', '.join(categories)}

Text:
{text[:2000]}

Return a JSON object with:
- "categories": list of selected category/categories
- "reasoning": brief explanation

Example: {{"categories": ["category1"], "reasoning": "because..."}}
"""

        try:
            response = self.generate_text(
                prompt=prompt,
                max_tokens=200,
                temperature=0.2
            )

            # Parse JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            result = json.loads(response)

            if not multi_label and len(result.get("categories", [])) > 1:
                result["categories"] = [result["categories"][0]]

            return result

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {"categories": [], "reasoning": "Classification error"}

    def test_connection(self) -> bool:
        """
        Test GROQ API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.generate_text(
                prompt="Say 'OK' if you can read this.",
                max_tokens=10,
                temperature=0.0
            )

            logger.info("✅ GROQ API connection successful")
            logger.debug(f"Test response: {response}")
            return True

        except Exception as e:
            logger.error(f"❌ GROQ API connection failed: {e}")
            return False


# Convenience function for quick usage
def quick_generate(prompt: str, **kwargs) -> str:
    """
    Quick text generation without creating client instance.

    Args:
        prompt: Text prompt
        **kwargs: Additional arguments for generate_text()

    Returns:
        Generated text
    """
    client = GROQClient()
    return client.generate_text(prompt, **kwargs)


if __name__ == "__main__":
    # Test the GROQ client
    from ..utils.logger import setup_logger

    setup_logger()

    logger.info("Testing GROQ Client...")

    client = GROQClient()

    # Test 1: Connection
    logger.info("\n=== Test 1: Connection ===")
    client.test_connection()

    # Test 2: Text generation
    logger.info("\n=== Test 2: Text Generation ===")
    response = client.generate_text(
        prompt="Explain thermal conductivity in materials in one sentence.",
        max_tokens=100
    )
    logger.info(f"Response: {response}")

    # Test 3: Entity extraction
    logger.info("\n=== Test 3: Entity Extraction ===")
    test_text = """
    Graphene exhibits exceptional thermal conductivity of 5000 W/mK and
    excellent electrical properties. We synthesized it using chemical vapor
    deposition (CVD) and characterized it with Raman spectroscopy.
    """
    entities = client.extract_entities(test_text)
    logger.info(f"Entities: {json.dumps(entities, indent=2)}")

    # Test 4: Summarization
    logger.info("\n=== Test 4: Summarization ===")
    summary = client.summarize_text(test_text, max_summary_length=30)
    logger.info(f"Summary: {summary}")

    logger.info("\n✨ All GROQ tests completed!")
