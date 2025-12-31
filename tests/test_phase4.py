"""
Quick test of Phase 4 components
"""

import sys
from pathlib import Path

# Test without imports first - just verify files exist


def test_files_exist():
    """Test that all Phase 4 files were created"""
    logger_available = False
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from utils.logger import setup_logger
        logger = setup_logger()
        logger_available = True
    except:
        logger = None
        print("Testing Phase 4 files...")

    base_path = Path(__file__).parent.parent

    files_to_check = [
        "src/api/api_key_rotator.py",
        "src/experiments/hypothesis_tester.py",
        "src/agent/autonomous_agent.py",
        "dashboard/app.py",
        "scripts/run_agent.py",
        "PHASE4_README.md"
    ]

    if logger_available:
        logger.info("="*60)
        logger.info("Testing Phase 4 File Creation")
        logger.info("="*60)
    else:
        print("="*60)
        print("Testing Phase 4 File Creation")
        print("="*60)

    all_exist = True
    for file_path in files_to_check:
        full_path = base_path / file_path
        exists = full_path.exists()
        all_exist = all_exist and exists

        status = "✓" if exists else "✗"
        if logger_available:
            if exists:
                logger.info(f"{status} {file_path}")
            else:
                logger.error(f"{status} {file_path}")
        else:
            print(f"{status} {file_path}")

    return all_exist


def test_api_rotation_logic():
    """Test API key rotation logic (without imports)"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from utils.logger import setup_logger
        logger = setup_logger()
        logger_available = True
    except:
        logger = None
        logger_available = True  # Proceed anyway
        print("\nTesting API Key Rotation Logic...")

    if logger_available and logger:
        logger.info("\n" + "="*60)
        logger.info("Testing API Key Rotation Logic")
        logger.info("="*60)

    # Read the api_key_rotator.py file to verify key components
    rotator_path = Path(__file__).parent.parent / "src/api/api_key_rotator.py"
    content = rotator_path.read_text()

    required_components = [
        "class APIKeyStatus",
        "class APIKeyRotator",
        "def get_current_key",
        "def mark_rate_limited",
        "def load_from_env",
        "with_key_rotation"
    ]

    all_present = True
    for component in required_components:
        present = component in content
        all_present = all_present and present
        status = "✓" if present else "✗"

        if logger_available and logger:
            if present:
                logger.info(f"{status} {component}")
            else:
                logger.error(f"{status} {component}")
        else:
            print(f"{status} {component}")

    return all_present


def test_components_structure():
    """Test that components have correct structure"""
    try:
        from utils.logger import setup_logger
        logger = setup_logger()
    except:
        logger = None
        print("\nTesting Component Structure...")

    if logger:
        logger.info("\n" + "="*60)
        logger.info("Testing Component Structure")
        logger.info("="*60)

    base_path = Path(__file__).parent.parent

    # Check hypothesis_tester.py
    tester_path = base_path / "src/experiments/hypothesis_tester.py"
    tester_content = tester_path.read_text()

    tester_components = [
        "class HypothesisTester",
        "def test_hypothesis",
        "def batch_test",
        "_test_via_materials_project",
        "_groq_analyze_evidence"
    ]

    if logger:
        logger.info("HypothesisTester components:")
    else:
        print("HypothesisTester components:")

    tester_ok = True
    for comp in tester_components:
        present = comp in tester_content
        tester_ok = tester_ok and present
        status = "  ✓" if present else "  ✗"

        if logger:
            if present:
                logger.info(f"{status} {comp}")
            else:
                logger.error(f"{status} {comp}")
        else:
            print(f"{status} {comp}")

    # Check autonomous_agent.py
    agent_path = base_path / "src/agent/autonomous_agent.py"
    agent_content = agent_path.read_text()

    agent_components = [
        "class AutonomousScientist",
        "def run",
        "_collect_papers",
        "_generate_hypotheses",
        "_test_hypotheses",
        "save_results"
    ]

    if logger:
        logger.info("\nAutonomousScientist components:")
    else:
        print("\nAutonomousScientist components:")

    agent_ok = True
    for comp in agent_components:
        present = comp in agent_content
        agent_ok = agent_ok and present
        status = "  ✓" if present else "  ✗"

        if logger:
            if present:
                logger.info(f"{status} {comp}")
            else:
                logger.error(f"{status} {comp}")
        else:
            print(f"{status} {comp}")

    return tester_ok and agent_ok


def main():
    """Run all Phase 4 tests"""
    try:
        from utils.logger import setup_logger
        logger = setup_logger()
        logger.info("🚀 Starting Phase 4 Component Tests\n")
    except:
        logger = None
        print("🚀 Starting Phase 4 Component Tests\n")

    results = []

    # Test 1: Files exist
    try:
        results.append(("File Creation", test_files_exist()))
    except Exception as e:
        if logger:
            logger.error(f"File test failed: {e}")
        else:
            print(f"File test failed: {e}")
        results.append(("File Creation", False))

    # Test 2: API Rotation logic
    try:
        results.append(("API Rotation Logic", test_api_rotation_logic()))
    except Exception as e:
        if logger:
            logger.error(f"API rotation test failed: {e}")
        else:
            print(f"API rotation test failed: {e}")
        results.append(("API Rotation Logic", False))

    # Test 3: Component structure
    try:
        results.append(("Component Structure", test_components_structure()))
    except Exception as e:
        if logger:
            logger.error(f"Component test failed: {e}")
        else:
            print(f"Component test failed: {e}")
        results.append(("Component Structure", False))

    # Summary
    if logger:
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
    else:
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if logger:
            logger.info(f"{status} - {name}")
        else:
            print(f"{status} - {name}")

    if logger:
        logger.info(f"\nResults: {passed}/{total} tests passed")
    else:
        print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        if logger:
            logger.success("\n🎉 All Phase 4 files created successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Configure API keys in .env file")
            logger.info("2. Run: python scripts/run_agent.py")
            logger.info("3. View dashboard: streamlit run dashboard/app.py")
        else:
            print("\n🎉 All Phase 4 files created successfully!")
            print("\nNext steps:")
            print("1. Configure API keys in .env file")
            print("2. Run: python scripts/run_agent.py")
            print("3. View dashboard: streamlit run dashboard/app.py")
    else:
        if logger:
            logger.warning("\n⚠️ Some tests failed. Check errors above.")
        else:
            print("\n⚠️ Some tests failed. Check errors above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
