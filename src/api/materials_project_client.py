"""
Materials Project API Client
============================
Wrapper for Materials Project v3 API with caching and error handling.
"""

import requests
from typing import Optional, Dict, Any, List
from pathlib import Path
from loguru import logger

from ..utils.rate_limiter import RateLimiter
from ..utils.retry import retry_with_backoff
from ..utils.helpers import save_json, load_json


class MaterialsProjectError(Exception):
    """Raised when Materials Project API returns an error."""
    pass


class MaterialsProjectClient:
    """
    Client for Materials Project v3 API.

    Provides access to materials science database with automatic caching
    to preserve API quota and improve performance.

    Attributes:
        api_key: Materials Project API key
        base_url: API endpoint base URL
        cache_dir: Directory for caching responses
        rate_limiter: Rate limiter instance for API calls

    Example:
        >>> client = MaterialsProjectClient(api_key="your_key")
        >>> material = client.search_by_formula("Fe2O3")
        >>> properties = client.get_material_properties("mp-19770")
    """

    def __init__(
        self,
        api_key: str,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True,
        requests_per_second: float = 5.0
    ):
        """
        Initialize Materials Project client.

        Args:
            api_key: Materials Project API key
            cache_dir: Directory for caching (default: data/cache)
            enable_cache: Whether to use local caching
            requests_per_second: Rate limit (default: 5.0)
        """
        self.api_key = api_key
        self.base_url = "https://api.materialsproject.org"
        self.enable_cache = enable_cache
        self.rate_limiter = RateLimiter(calls_per_second=requests_per_second)

        # Set up cache directory
        if cache_dir is None:
            # Default to data/cache relative to project root
            current_dir = Path(__file__).resolve().parent
            cache_dir = current_dir.parents[1] / \
                "data" / "cache" / "materials_project"

        self.cache_dir = Path(cache_dir)
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized MaterialsProjectClient (cache: {enable_cache})")

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a given key."""
        # Sanitize cache key for filename
        safe_key = "".join(c if c.isalnum() else "_" for c in cache_key)
        return self.cache_dir / f"{safe_key}.json"

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Retrieve cached response if available."""
        if not self.enable_cache:
            return None

        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            logger.debug(f"Cache hit: {cache_key}")
            return load_json(cache_path)
        return None

    def _save_cache(self, cache_key: str, data: Any) -> None:
        """Save response to cache."""
        if not self.enable_cache:
            return

        cache_path = self._get_cache_path(cache_key)
        save_json(data, cache_path)
        logger.debug(f"Cached: {cache_key}")

    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        exceptions=(requests.exceptions.RequestException,
                    MaterialsProjectError)
    )
    def search_by_formula(
        self,
        formula: str,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for materials by chemical formula.

        Args:
            formula: Chemical formula (e.g., "Fe2O3", "NaCl")
            fields: List of fields to return (default: basic properties)

        Returns:
            List of matching materials with requested properties

        Raises:
            MaterialsProjectError: If API returns an error

        Example:
            >>> results = client.search_by_formula("Fe2O3")
            >>> for material in results:
            ...     print(material["material_id"], material["formula_pretty"])
        """
        # Check cache first
        cache_key = f"formula_{formula}_{'_'.join(fields or [])}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Apply rate limiting
        self.rate_limiter.wait()

        # Default fields if none specified
        if fields is None:
            fields = [
                "material_id",
                "formula_pretty",
                "formula_anonymous",
                "symmetry",
                "band_gap",
                "energy_above_hull",
                "formation_energy_per_atom",
                "density",
            ]

        # Build request URL
        url = f"{self.base_url}/materials/summary/"

        # Build query parameters
        params = {
            "formula": formula,
            "_fields": ",".join(fields),
            "_limit": 100
        }

        logger.debug(f"Searching Materials Project for formula: {formula}")

        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            error_msg = f"Materials Project API HTTP error: {e}"
            if response.text:
                error_msg += f"\nResponse: {response.text}"
            logger.error(error_msg)
            raise MaterialsProjectError(error_msg)

        except requests.exceptions.RequestException as e:
            logger.error(f"Materials Project API request failed: {e}")
            raise

        # Parse response
        try:
            data = response.json()

            if "data" not in data:
                raise MaterialsProjectError("No 'data' field in response")

            results = data["data"]
            logger.info(
                f"Found {len(results)} materials for formula {formula}")

            # Cache the results
            self._save_cache(cache_key, results)

            return results

        except (KeyError, ValueError) as e:
            logger.error(f"Failed to parse Materials Project response: {e}")
            raise MaterialsProjectError(f"Response parsing error: {e}")

    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        exceptions=(requests.exceptions.RequestException,
                    MaterialsProjectError)
    )
    def get_material_properties(
        self,
        material_id: str,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed properties for a specific material.

        Args:
            material_id: Material ID (e.g., "mp-19770")
            fields: List of fields to return (default: comprehensive set)

        Returns:
            Dictionary of material properties

        Example:
            >>> props = client.get_material_properties("mp-19770")
            >>> print(props["formula_pretty"], props["band_gap"])
        """
        # Check cache first
        cache_key = f"material_{material_id}_{'_'.join(fields or [])}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Apply rate limiting
        self.rate_limiter.wait()

        # Default fields if none specified
        if fields is None:
            fields = [
                "material_id",
                "formula_pretty",
                "symmetry",
                "band_gap",
                "energy_above_hull",
                "formation_energy_per_atom",
                "density",
                "theoretical",
                "nelements",
                "elements",
            ]

        # Build request URL
        url = f"{self.base_url}/materials/summary/{material_id}/"

        params = {
            "_fields": ",".join(fields)
        }

        logger.debug(f"Getting properties for material: {material_id}")

        try:
            response = requests.get(
                url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if "data" not in data or not data["data"]:
                raise MaterialsProjectError(
                    f"Material {material_id} not found")

            properties = data["data"][0]
            logger.info(f"Retrieved properties for {material_id}")

            # Cache the results
            self._save_cache(cache_key, properties)

            return properties

        except Exception as e:
            logger.error(f"Failed to get material properties: {e}")
            raise MaterialsProjectError(f"Error getting properties: {e}")

    def test_connection(self) -> bool:
        """
        Test if API key is valid and connection works.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Search for a common material (water ice)
            results = self.search_by_formula("H2O")
            logger.info(
                f"Materials Project API connection test: SUCCESS ({len(results)} results)")
            return True
        except Exception as e:
            logger.error(f"Materials Project API connection test failed: {e}")
            return False
