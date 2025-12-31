"""
Integration test for Phase 4 - Test complete system
"""

import pandas as pd
from utils.logger import setup_logger
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


logger = setup_logger()


def test_api_rotation_instantiation():
    """Test that API rotation system can be instantiated"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: API Key Rotation Instantiation")
    logger.info("="*60)

    try:
        # Import and test without actual API calls
        from api.api_key_rotator import APIKeyRotator, APIKeyStatus

        # Create rotator with mock keys
        rotator = APIKeyRotator(["key1", "key2", "key3"])

        # Test basic operations
        current_key = rotator.get_current_key()
        logger.info(f"✓ Current key retrieved: {current_key}")

        # Test rotation
        rotator.mark_rate_limited(current_key)
        new_key = rotator.get_current_key()
        logger.info(f"✓ Rotated to new key: {new_key}")

        assert current_key != new_key, "Keys should be different after rotation"
        logger.success("✅ API Rotation system works!")
        return True

    except Exception as e:
        logger.error(f"❌ API Rotation test failed: {e}")
        return False


def test_hypothesis_tester_import():
    """Test that hypothesis tester can be imported"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Hypothesis Tester Import")
    logger.info("="*60)

    try:
        from experiments.hypothesis_tester import HypothesisTester

        logger.info("✓ HypothesisTester imported successfully")

        # Verify class has required methods
        required_methods = ['test_hypothesis',
                            'batch_test', '_test_via_materials_project']
        for method in required_methods:
            assert hasattr(HypothesisTester,
                           method), f"Missing method: {method}"
            logger.info(f"✓ Method exists: {method}")

        logger.success("✅ Hypothesis Tester structure validated!")
        return True

    except Exception as e:
        logger.error(f"❌ Hypothesis Tester test failed: {e}")
        return False


def test_autonomous_agent_import():
    """Test that autonomous agent can be imported"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Autonomous Agent Import")
    logger.info("="*60)

    try:
        from agent.autonomous_agent import AutonomousScientist

        logger.info("✓ AutonomousScientist imported successfully")

        # Verify class has required methods
        required_methods = ['run', '_collect_papers', '_generate_hypotheses',
                            '_test_hypotheses', 'save_results']
        for method in required_methods:
            assert hasattr(AutonomousScientist,
                           method), f"Missing method: {method}"
            logger.info(f"✓ Method exists: {method}")

        logger.success("✅ Autonomous Agent structure validated!")
        return True

    except Exception as e:
        logger.error(f"❌ Autonomous Agent test failed: {e}")
        return False


def test_dashboard_file():
    """Test that dashboard file exists and has key components"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Dashboard Validation")
    logger.info("="*60)

    try:
        dashboard_path = Path(__file__).parent.parent / "dashboard/app.py"

        assert dashboard_path.exists(), "Dashboard file not found"
        logger.info("✓ Dashboard file exists")

        content = dashboard_path.read_text()

        # Check for key Streamlit components
        required_components = [
            'st.set_page_config',
            'st.tabs',
            'streamlit',
            'plotly',
            'Overview',
            'Papers',
            'Hypotheses'
        ]

        for component in required_components:
            assert component in content, f"Missing component: {component}"
            logger.info(f"✓ Component found: {component}")

        logger.success("✅ Dashboard structure validated!")
        return True

    except Exception as e:
        logger.error(f"❌ Dashboard test failed: {e}")
        return False


def test_run_script():
    """Test that run script exists and is properly structured"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Run Script Validation")
    logger.info("="*60)

    try:
        script_path = Path(__file__).parent.parent / "scripts/run_agent.py"

        assert script_path.exists(), "Run script not found"
        logger.info("✓ Run script exists")

        content = script_path.read_text()

        # Check for key components
        required_parts = [
            'AutonomousScientist',
            'agent.run',
            'agent.save_results',
            'if __name__ == "__main__"'
        ]

        for part in required_parts:
            assert part in content, f"Missing part: {part}"
            logger.info(f"✓ Found: {part}")

        logger.success("✅ Run script validated!")
        return True

    except Exception as e:
        logger.error(f"❌ Run script test failed: {e}")
        return False


def test_data_flow():
    """Test that data structures work correctly"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Data Flow Validation")
    logger.info("="*60)

    try:
        # Create sample data structures
        papers = pd.DataFrame([{
            'title': 'Test Paper',
            'authors': 'Test Author',
            'summary': 'Test summary'
        }])

        hypotheses = pd.DataFrame([{
            'hypothesis': 'Test hypothesis',
            'materials': 'LiCoO2',
            'method': 'Test method',
            'expected_outcome': 'Test outcome'
        }])

        logger.info(f"✓ Created papers DataFrame: {len(papers)} rows")
        logger.info(f"✓ Created hypotheses DataFrame: {len(hypotheses)} rows")

        # Test data can be saved/loaded
        test_dir = Path(__file__).parent.parent / "data/test_output"
        test_dir.mkdir(parents=True, exist_ok=True)

        papers.to_csv(test_dir / "test_papers.csv", index=False)
        hypotheses.to_csv(test_dir / "test_hypotheses.csv", index=False)

        loaded_papers = pd.read_csv(test_dir / "test_papers.csv")
        loaded_hypotheses = pd.read_csv(test_dir / "test_hypotheses.csv")

        assert len(loaded_papers) == len(papers), "Papers data mismatch"
        assert len(loaded_hypotheses) == len(
            hypotheses), "Hypotheses data mismatch"

        logger.info("✓ Data can be saved and loaded")

        # Cleanup
        (test_dir / "test_papers.csv").unlink()
        (test_dir / "test_hypotheses.csv").unlink()
        test_dir.rmdir()

        logger.success("✅ Data flow validated!")
        return True

    except Exception as e:
        logger.error(f"❌ Data flow test failed: {e}")
        return False


def main():
    """Run all integration tests"""
    logger.info("🚀 Starting Phase 4 Integration Tests\n")

    tests = [
        ("API Rotation", test_api_rotation_instantiation),
        ("Hypothesis Tester", test_hypothesis_tester_import),
        ("Autonomous Agent", test_autonomous_agent_import),
        ("Dashboard", test_dashboard_file),
        ("Run Script", test_run_script),
        ("Data Flow", test_data_flow)
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test {name} crashed: {e}")
            results.append((name, False))

    # Summary
    logger.info("\n" + "="*60)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")

    logger.info(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        logger.success("\n🎉 All integration tests passed!")
        logger.info("\n✨ Phase 4 System Status: FULLY OPERATIONAL")
        logger.info("\nYou can now:")
        logger.info("1. View dashboard at: http://localhost:8501")
        logger.info("2. Run autonomous research: python scripts/run_agent.py")
        logger.info("3. Explore results in the web interface")
    else:
        logger.warning(f"\n⚠️ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
