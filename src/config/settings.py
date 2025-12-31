"""
Settings Management for Autonomous Scientific Agent
===================================================
Loads configuration from .env file and provides validated access to all settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class SettingsError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Settings:
    """
    Configuration settings loader and validator.

    Loads API keys and configuration from .env file, validates their presence,
    and provides type-safe access to all settings.

    Attributes:
        gemini_api_key: Google Gemini API key
        hf_token: Hugging Face API token
        mp_api_key: Materials Project API key
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        cache_enabled: Whether to cache API responses
        max_retries: Maximum retry attempts for failed API calls
        request_timeout: Timeout for API requests in seconds

    Example:
        >>> settings = Settings()
        >>> settings.validate_all()
        >>> client = GeminiClient(settings.gemini_api_key)
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize settings by loading from .env file.

        Args:
            env_file: Path to .env file. If None, searches for .env in project root.

        Raises:
            SettingsError: If .env file cannot be found or loaded.
        """
        # Find project root (where .env should be)
        if env_file:
            env_path = Path(env_file)
        else:
            # Look for .env starting from current file's directory
            current_dir = Path(__file__).resolve().parent
            env_path = None

            # Search up the directory tree
            for parent in [current_dir] + list(current_dir.parents):
                candidate = parent / ".env"
                if candidate.exists():
                    env_path = candidate
                    break

        # Load environment variables
        if env_path and env_path.exists():
            load_dotenv(env_path)
            self._env_file_path = str(env_path)
        else:
            # Try loading from default location anyway
            load_dotenv()
            self._env_file_path = ".env (default location)"

        # Load API keys
        self._gemini_api_key = os.getenv("GEMINI_API_KEY")
        self._hf_token = os.getenv("HF_TOKEN")
        self._mp_api_key = os.getenv("MP_API_KEY")
        self._groq_api_key = os.getenv("GROQ_API_KEY")

        # Load optional settings with defaults
        self._log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self._cache_enabled = os.getenv(
            "CACHE_ENABLED", "true").lower() == "true"
        self._max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self._request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))

    @property
    def gemini_api_key(self) -> str:
        """
        Get Google Gemini API key.

        Returns:
            The API key string.

        Raises:
            SettingsError: If the key is not set.
        """
        if not self._gemini_api_key or self._gemini_api_key == "your_gemini_key_here":
            raise SettingsError(
                "GEMINI_API_KEY not set in .env file. "
                "See API_SETUP_GUIDE.md for instructions."
            )
        return self._gemini_api_key

    @property
    def hf_token(self) -> str:
        """
        Get Hugging Face API token.

        Returns:
            The API token string.

        Raises:
            SettingsError: If the token is not set.
        """
        if not self._hf_token or self._hf_token == "your_huggingface_token_here":
            raise SettingsError(
                "HF_TOKEN not set in .env file. "
                "See API_SETUP_GUIDE.md for instructions."
            )
        return self._hf_token

    @property
    def mp_api_key(self) -> str:
        """
        Get Materials Project API key.

        Returns:
            The API key string.

        Raises:
            SettingsError: If the key is not set.
        """
        if not self._mp_api_key or self._mp_api_key == "your_materials_project_key_here":
            raise SettingsError(
                "MP_API_KEY not set in .env file. "
                "See API_SETUP_GUIDE.md for instructions."
            )
        return self._mp_api_key

    @property
    def groq_api_key(self) -> str:
        """
        Get GROQ API key.

        Returns:
            The API key string.

        Raises:
            SettingsError: If the key is not set.
        """
        if not self._groq_api_key or self._groq_api_key == "your_groq_key_here":
            raise SettingsError(
                "GROQ_API_KEY not set in .env file. "
                "Get your key from https://console.groq.com/"
            )
        return self._groq_api_key

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return self._log_level

    @property
    def cache_enabled(self) -> bool:
        """Check if response caching is enabled."""
        return self._cache_enabled

    @property
    def max_retries(self) -> int:
        """Get maximum retry attempts for API calls."""
        return self._max_retries

    @property
    def request_timeout(self) -> int:
        """Get request timeout in seconds."""
        return self._request_timeout

    def validate_all(self) -> dict[str, bool]:
        """
        Validate all required API keys are present and properly configured.

        Returns:
            Dictionary mapping API names to validation status.
            Example: {"gemini": True, "groq": True, "huggingface": False, "materials_project": True}

        Raises:
            SettingsError: If any required key is missing or invalid.
        """
        results = {}
        errors = []

        # Check each API key
        try:
            _ = self.gemini_api_key
            results["gemini"] = True
        except SettingsError as e:
            results["gemini"] = False
            errors.append(str(e))

        try:
            _ = self.groq_api_key
            results["groq"] = True
        except SettingsError as e:
            results["groq"] = False
            errors.append(str(e))

        try:
            _ = self.hf_token
            results["huggingface"] = True
        except SettingsError as e:
            results["huggingface"] = False
            errors.append(str(e))

        try:
            _ = self.mp_api_key
            results["materials_project"] = True
        except SettingsError as e:
            results["materials_project"] = False
            errors.append(str(e))

        # If any keys are missing, raise error with all messages
        if errors:
            raise SettingsError(
                f"Configuration validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        return results

    def get_cache_dir(self) -> Path:
        """
        Get the cache directory path.

        Returns:
            Path object pointing to cache directory.
        """
        cache_dir = Path(__file__).resolve().parents[2] / "data" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def __repr__(self) -> str:
        """String representation of settings (without exposing keys)."""
        return (
            f"Settings(\n"
            f"  env_file='{self._env_file_path}',\n"
            f"  gemini_configured={bool(self._gemini_api_key and self._gemini_api_key != 'your_gemini_key_here')},\n"
            f"  groq_configured={bool(self._groq_api_key and self._groq_api_key != 'your_groq_key_here')},\n"
            f"  hf_configured={bool(self._hf_token and self._hf_token != 'your_huggingface_token_here')},\n"
            f"  mp_configured={bool(self._mp_api_key and self._mp_api_key != 'your_materials_project_key_here')},\n"
            f"  log_level='{self._log_level}',\n"
            f"  cache_enabled={self._cache_enabled},\n"
            f"  max_retries={self._max_retries},\n"
            f"  request_timeout={self._request_timeout}\n"
            f")"
        )
