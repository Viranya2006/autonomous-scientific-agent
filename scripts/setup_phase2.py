"""
Phase 2 Setup Script

This script helps you set up Phase 2 by:
1. Checking for required dependencies
2. Verifying API keys
3. Testing connections
4. Running a quick demo

Run: python scripts/setup_phase2.py
"""

from loguru import logger
from src.config.settings import Settings, SettingsError
from src.utils.logger import setup_logger
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def check_dependencies():
    """Check if all required packages are installed."""
    logger.info("Checking dependencies...")

    required = [
        ("networkx", "NetworkX"),
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn"),
        ("pandas", "Pandas"),
        ("requests", "Requests")
    ]

    missing = []
    for module, name in required:
        try:
            __import__(module)
            logger.info(f"  ✅ {name}")
        except ImportError:
            logger.warning(f"  ❌ {name} - Not installed")
            missing.append(module)

    if missing:
        logger.warning(f"\nMissing packages: {', '.join(missing)}")
        logger.info(f"Install with: pip install {' '.join(missing)}")
        return False

    logger.info("✅ All dependencies installed!\n")
    return True


def check_api_keys():
    """Check if API keys are configured."""
    logger.info("Checking API configuration...")

    try:
        settings = Settings()

        # Check Gemini
        try:
            _ = settings.gemini_api_key
            logger.info("  ✅ Gemini API key configured")
        except SettingsError:
            logger.warning("  ❌ Gemini API key missing")

        # Check GROQ
        try:
            _ = settings.groq_api_key
            logger.info("  ✅ GROQ API key configured")
        except SettingsError:
            logger.warning(
                "  ❌ GROQ API key missing (get from https://console.groq.com/)")

        # Check Materials Project
        try:
            _ = settings.mp_api_key
            logger.info("  ✅ Materials Project API key configured")
        except SettingsError:
            logger.warning(
                "  ⚠️  Materials Project API key missing (optional for Phase 2)")

        logger.info("")
        return True

    except Exception as e:
        logger.error(f"Configuration error: {e}")
        return False


def test_connections():
    """Test API connections."""
    logger.info("Testing API connections...\n")

    # Test Gemini
    try:
        from src.api.gemini_client import GeminiClient
        from src.config.settings import Settings

        logger.info("Testing Gemini API...")
        settings = Settings()
        gemini = GeminiClient(api_key=settings.gemini_api_key)
        if gemini.test_connection():
            logger.info("  ✅ Gemini connection successful\n")
        else:
            logger.warning("  ❌ Gemini connection failed\n")
    except Exception as e:
        logger.error(f"  ❌ Gemini error: {e}\n")

    # Test GROQ
    try:
        from src.api.groq_client import GROQClient

        logger.info("Testing GROQ API...")
        groq = GROQClient()
        if groq.test_connection():
            logger.info("  ✅ GROQ connection successful\n")
        else:
            logger.warning("  ❌ GROQ connection failed\n")
    except Exception as e:
        logger.error(f"  ❌ GROQ error: {e}\n")


def run_quick_demo():
    """Run a quick demo of Phase 2 capabilities."""
    logger.info("Running quick demo...\n")

    try:
        from src.data_collection import ArXivCollector
        from src.analysis import PaperAnalyzer, KnowledgeExtractor

        # Collect a few papers
        logger.info("📚 Collecting sample papers...")
        collector = ArXivCollector()
        papers = collector.search(
            query="graphene",
            max_results=3,
            categories=["cond-mat.mtrl-sci"]
        )
        logger.info(f"  Found {len(papers)} papers\n")

        if len(papers) == 0:
            logger.warning(
                "  No papers found. Check your internet connection.")
            return False

        # Analyze one paper
        logger.info("🤖 Analyzing first paper with AI...")
        analyzer = PaperAnalyzer()
        analysis = analyzer.analyze_paper(papers[0])

        logger.info(f"  Title: {analysis.title[:60]}...")
        logger.info(f"  Relevance: {analysis.relevance_score:.1f}/10")
        logger.info(f"  Materials: {', '.join(analysis.materials[:5])}")
        logger.info(f"  Properties: {', '.join(analysis.properties[:5])}\n")

        # Build mini knowledge graph
        logger.info("🧠 Building knowledge graph...")
        extractor = KnowledgeExtractor()
        analyses = [analysis]
        graph = extractor.build_knowledge_graph(analyses)

        stats = extractor.get_graph_statistics()
        logger.info(f"  Nodes: {stats['total_nodes']}")
        logger.info(f"  Edges: {stats['total_edges']}\n")

        logger.info("✨ Demo completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup flow."""
    setup_logger(log_level="INFO")

    logger.info("=" * 80)
    logger.info("AUTONOMOUS SCIENTIFIC AGENT - Phase 2 Setup")
    logger.info("=" * 80)
    logger.info("")

    # Step 1: Check dependencies
    if not check_dependencies():
        logger.error("\n❌ Setup failed: Missing dependencies")
        logger.info("\nInstall missing packages with:")
        logger.info("  pip install networkx matplotlib seaborn jupyter")
        return 1

    # Step 2: Check API keys
    check_api_keys()

    # Step 3: Test connections
    logger.info("Do you want to test API connections? (y/n): ", end="")
    response = input().strip().lower()
    if response == 'y':
        test_connections()

    # Step 4: Run demo
    logger.info("Do you want to run a quick demo? (y/n): ", end="")
    response = input().strip().lower()
    if response == 'y':
        logger.info("")
        if run_quick_demo():
            logger.info("\n" + "=" * 80)
            logger.info("🎉 Phase 2 is ready to use!")
            logger.info("=" * 80)
            logger.info("\nNext steps:")
            logger.info(
                "  1. Read PHASE2_README.md for detailed documentation")
            logger.info(
                "  2. Run: python scripts/collect_and_analyze.py --query 'your topic' --max-papers 20")
            logger.info(
                "  3. Explore results in: jupyter notebook notebooks/02_phase2_exploration.ipynb")
            logger.info("")
        else:
            logger.error(
                "\n❌ Demo failed. Check your API keys and internet connection.")
            return 1
    else:
        logger.info("\n" + "=" * 80)
        logger.info("Setup complete! Read PHASE2_README.md to get started.")
        logger.info("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
