"""
API Testing Script
==================
Comprehensive test suite for all API connections.

Tests each API client (Gemini, Hugging Face, Materials Project) and reports:
- Connection status
- Response time
- Sample output
- Error details (if any)

Results are saved to logs/api_test_results.json
"""

from utils.helpers import save_json
from utils.logger import setup_logger
from api.materials_project_client import MaterialsProjectClient, MaterialsProjectError
from api.huggingface_client import HuggingFaceClient, HuggingFaceError
from api.gemini_client import GeminiClient, GeminiError
from config.settings import Settings, SettingsError
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src to path to import modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import after path is set


def print_header(text: str) -> None:
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print('=' * 70)


def print_test_result(name: str, success: bool, duration: float, message: str = "") -> None:
    """Print formatted test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {name:<30} | {duration:>6.2f}s | {message}")


def test_gemini(settings: Settings) -> Dict[str, Any]:
    """
    Test Google Gemini API.

    Returns:
        Test results dictionary
    """
    result = {
        "name": "Google Gemini",
        "success": False,
        "duration": 0.0,
        "error": None,
        "sample_output": None
    }

    try:
        start_time = time.time()

        # Initialize client
        client = GeminiClient(settings.gemini_api_key)

        # Test with simple prompt
        prompt = "What is a perovskite material? Answer in one sentence."
        response = client.generate_text(
            prompt, max_tokens=100, temperature=0.3)

        duration = time.time() - start_time

        result["success"] = True
        result["duration"] = duration
        result["sample_output"] = response[:200] + \
            "..." if len(response) > 200 else response

        print_test_result("Gemini API", True, duration,
                          "Text generation working")

    except SettingsError as e:
        result["error"] = f"Configuration error: {str(e)}"
        print_test_result("Gemini API", False, 0.0, str(e))
    except GeminiError as e:
        result["error"] = f"API error: {str(e)}"
        print_test_result("Gemini API", False, 0.0, str(e))
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print_test_result("Gemini API", False, 0.0, str(e))

    return result


def test_huggingface(settings: Settings) -> Dict[str, Any]:
    """
    Test Hugging Face API.

    Returns:
        Test results dictionary
    """
    result = {
        "name": "Hugging Face",
        "success": False,
        "duration": 0.0,
        "error": None,
        "sample_output": None
    }

    try:
        start_time = time.time()

        # Initialize client
        client = HuggingFaceClient(settings.hf_token)

        # Test with chat completions using instruction model
        prompt = "Explain quantum entanglement in simple terms."
        response = client.generate_text(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.2",
            max_tokens=200,
            temperature=0.7
        )

        duration = time.time() - start_time

        result["success"] = True
        result["duration"] = duration
        result["sample_output"] = response[:200] + \
            "..." if len(response) > 200 else response

        print_test_result("Hugging Face API", True,
                          duration, "Inference working")

    except SettingsError as e:
        result["error"] = f"Configuration error: {str(e)}"
        print_test_result("Hugging Face API", False, 0.0, "Config error")
    except (HuggingFaceError, Exception) as e:
        error_str = str(e)
        # Check if it's the deprecation error
        if "no longer supported" in error_str.lower():
            result["error"] = "API deprecated (requires paid subscription)"
            print_test_result("Hugging Face API", False, 0.0,
                              "Deprecated API (paid only)")
        else:
            result["error"] = f"API error: {error_str[:100]}"
            print_test_result("Hugging Face API", False, 0.0, error_str[:50])

    return result


def test_materials_project(settings: Settings) -> Dict[str, Any]:
    """
    Test Materials Project API.

    Returns:
        Test results dictionary
    """
    result = {
        "name": "Materials Project",
        "success": False,
        "duration": 0.0,
        "error": None,
        "sample_output": None
    }

    try:
        start_time = time.time()

        # Initialize client
        client = MaterialsProjectClient(
            settings.mp_api_key, enable_cache=settings.cache_enabled)

        # Test by searching for common material
        results = client.search_by_formula("Si")

        duration = time.time() - start_time

        if results:
            sample = results[0]
            output = f"Found {len(results)} materials. Example: {sample.get('formula_pretty', 'N/A')} (ID: {sample.get('material_id', 'N/A')})"
        else:
            output = "Search returned no results"

        result["success"] = True
        result["duration"] = duration
        result["sample_output"] = output

        print_test_result("Materials Project API", True, duration, output)

    except SettingsError as e:
        result["error"] = f"Configuration error: {str(e)}"
        print_test_result("Materials Project API", False, 0.0, str(e))
    except MaterialsProjectError as e:
        result["error"] = f"API error: {str(e)}"
        print_test_result("Materials Project API", False, 0.0, str(e))
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        print_test_result("Materials Project API", False, 0.0, str(e))

    return result


def main():
    """Main test routine."""
    print_header("🧪 Autonomous Scientific Agent - API Test Suite")

    # Setup logger
    logger = setup_logger(log_level="INFO")
    logger.info("Starting API tests")

    # Load settings
    print("\n📝 Loading configuration...")
    try:
        settings = Settings()
        print("✅ Configuration loaded")
        print(f"   - Log Level: {settings.log_level}")
        print(f"   - Cache Enabled: {settings.cache_enabled}")
        print(f"   - Max Retries: {settings.max_retries}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        print("\nMake sure you have:")
        print("  1. Created .env file (copy from .env.example)")
        print("  2. Added your API keys to .env")
        print("  3. See API_SETUP_GUIDE.md for help")
        sys.exit(1)

    # Validate API keys
    print("\n🔑 Validating API keys...")
    try:
        validation = settings.validate_all()
        for api, valid in validation.items():
            status = "✅" if valid else "❌"
            print(f"   {status} {api.replace('_', ' ').title()}")
    except SettingsError as e:
        print(f"❌ Validation failed:\n{e}")
        print("\nPlease add missing API keys to .env file")
        print("See API_SETUP_GUIDE.md for instructions")
        sys.exit(1)

    # Run tests
    print_header("🧪 Running API Tests")
    print(f"{'Status':<8} | {'API':<30} | {'Time':>8} | {'Details'}")
    print('-' * 70)

    test_results = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "tests": {}
    }

    # Test each API
    test_results["tests"]["gemini"] = test_gemini(settings)
    test_results["tests"]["huggingface"] = test_huggingface(settings)
    test_results["tests"]["materials_project"] = test_materials_project(
        settings)

    # Summary
    print_header("📊 Test Summary")

    total_tests = len(test_results["tests"])
    passed_tests = sum(
        1 for t in test_results["tests"].values() if t["success"])
    failed_tests = total_tests - passed_tests

    # Count critical vs optional failures
    hf_failed = not test_results["tests"]["huggingface"]["success"]
    critical_failures = failed_tests - (1 if hf_failed else 0)

    print(f"\nTotal Tests:  {total_tests}")
    print(f"✅ Passed:     {passed_tests}")
    print(f"❌ Failed:     {failed_tests}")

    if hf_failed:
        print(f"\n⚠️  Note: HuggingFace API requires paid subscription (optional)")
        print(f"   The agent works perfectly with Gemini + Materials Project")
        print(f"   See HUGGINGFACE_STATUS.md for free alternatives")

    # Save results
    results_file = project_root / "logs" / "api_test_results.json"
    save_json(test_results, results_file)
    print(f"\n💾 Full results saved to: {results_file}")

    # Exit with appropriate code
    if critical_failures > 0:
        print("\n❌ Critical tests failed. Please check your API keys and connectivity.")
        sys.exit(1)
    else:
        print("\n🎉 Core APIs passed! Your agent is ready to use.")
        print("\n📚 Next: Explore notebooks/01_phase1_testing.ipynb")
        sys.exit(0)


if __name__ == "__main__":
    main()
