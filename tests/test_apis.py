"""
Unit Tests for API Clients
==========================
Pytest-based unit tests for all API client wrappers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

# Import clients
from src.api.gemini_client import GeminiClient, GeminiError
from src.api.huggingface_client import HuggingFaceClient, HuggingFaceError
from src.api.materials_project_client import MaterialsProjectClient, MaterialsProjectError
from src.config.settings import Settings, SettingsError


class TestSettings:
    """Test suite for Settings class."""

    def test_settings_initialization(self):
        """Test that settings can be initialized."""
        # This will try to load from .env
        settings = Settings()
        assert settings is not None

    def test_settings_properties(self):
        """Test that settings have required properties."""
        settings = Settings()

        # Check that properties exist (they may raise errors if not configured)
        assert hasattr(settings, 'log_level')
        assert hasattr(settings, 'cache_enabled')
        assert hasattr(settings, 'max_retries')
        assert hasattr(settings, 'request_timeout')

    def test_get_cache_dir(self):
        """Test cache directory creation."""
        settings = Settings()
        cache_dir = settings.get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir.name == "cache"


class TestGeminiClient:
    """Test suite for GeminiClient."""

    def test_client_initialization(self):
        """Test Gemini client can be initialized."""
        client = GeminiClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.model == "gemini-2.5-flash"

    def test_build_url(self):
        """Test URL construction."""
        client = GeminiClient(api_key="test_key_123")
        url = client._build_url("models/test")
        assert "test_key_123" in url
        assert "models/test" in url

    def test_count_tokens(self):
        """Test token counting estimation."""
        client = GeminiClient(api_key="test_key")
        text = "This is a test" * 100
        tokens = client.count_tokens(text)
        assert tokens > 0
        assert tokens == len(text) // 4

    @patch('requests.post')
    def test_generate_text_success(self, mock_post):
        """Test successful text generation."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "This is a test response"}]
                }
            }]
        }
        mock_post.return_value = mock_response

        client = GeminiClient(api_key="test_key")
        result = client.generate_text("test prompt")

        assert result == "This is a test response"
        assert mock_post.called

    @patch('requests.post')
    def test_generate_text_error(self, mock_post):
        """Test error handling in text generation."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        client = GeminiClient(api_key="test_key")

        with pytest.raises(GeminiError):
            client.generate_text("test prompt")


class TestHuggingFaceClient:
    """Test suite for HuggingFaceClient."""

    def test_client_initialization(self):
        """Test HuggingFace client can be initialized."""
        client = HuggingFaceClient(token="test_token")
        assert client.token == "test_token"
        assert "api-inference.huggingface.co" in client.base_url

    def test_get_headers(self):
        """Test header construction."""
        client = HuggingFaceClient(token="test_token_123")
        headers = client._get_headers()
        assert "Authorization" in headers
        assert "test_token_123" in headers["Authorization"]

    @patch('requests.post')
    def test_generate_text_success(self, mock_post):
        """Test successful text generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"generated_text": "Generated response"}
        ]
        mock_post.return_value = mock_response

        client = HuggingFaceClient(token="test_token")
        result = client.generate_text("test prompt", model="gpt2")

        assert result == "Generated response"
        assert mock_post.called


class TestMaterialsProjectClient:
    """Test suite for MaterialsProjectClient."""

    def test_client_initialization(self):
        """Test Materials Project client can be initialized."""
        client = MaterialsProjectClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "materialsproject.org" in client.base_url

    def test_get_headers(self):
        """Test header construction."""
        client = MaterialsProjectClient(api_key="test_key_123")
        headers = client._get_headers()
        assert "X-API-KEY" in headers
        assert headers["X-API-KEY"] == "test_key_123"

    def test_cache_path_generation(self):
        """Test cache path creation."""
        client = MaterialsProjectClient(api_key="test_key", enable_cache=True)
        cache_path = client._get_cache_path("test_query")
        assert cache_path.suffix == ".json"
        assert "test_query" in str(cache_path)

    @patch('requests.get')
    def test_search_by_formula_success(self, mock_get):
        """Test successful material search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "material_id": "mp-149",
                    "formula_pretty": "Si",
                    "band_gap": 1.2
                }
            ]
        }
        mock_get.return_value = mock_response

        client = MaterialsProjectClient(api_key="test_key", enable_cache=False)
        results = client.search_by_formula("Si")

        assert len(results) == 1
        assert results[0]["formula_pretty"] == "Si"
        assert mock_get.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
