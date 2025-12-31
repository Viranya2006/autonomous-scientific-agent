"""
Quick test to verify system is working and analyze papers with GROQ only
"""
from src.utils.logger import setup_logger
from src.data_collection.paper_collector import ArXivCollector
from src.api.groq_client import GROQClient
from src.config.settings import Settings
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


setup_logger(log_level="INFO")

# Initialize
settings = Settings()
groq = GROQClient(api_key=settings.groq_api_key)
collector = ArXivCollector()

# Test GROQ
print("\n🧪 Testing GROQ API...")
try:
    response = groq.generate_text(
        "Say 'hello' in exactly 3 words", max_tokens=50)
    print(f"✅ GROQ is working: {response}")
except Exception as e:
    print(f"❌ GROQ failed: {e}")
    sys.exit(1)

# Collect papers
print("\n📚 Collecting 5 papers on battery materials...")
try:
    papers = collector.search(
        query="lithium battery materials",
        max_results=5,
        categories=["cond-mat.mtrl-sci"]
    )
    print(f"✅ Collected {len(papers)} papers")

    if papers:
        print("\n📄 Sample papers:")
        for i, paper in enumerate(papers[:3], 1):
            print(f"{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:2])}...")
            print(f"   ArXiv ID: {paper.arxiv_id}\n")

except Exception as e:
    print(f"❌ Paper collection failed: {e}")
    sys.exit(1)

# Test paper analysis with GROQ only
print("\n🤖 Testing paper analysis with GROQ...")
try:
    if papers:
        paper = papers[0]
        print(f"Analyzing: {paper.title[:80]}...")

        # Quick analysis with GROQ
        prompt = f"""Analyze this scientific paper briefly:
        
Title: {paper.title}
Abstract: {paper.abstract[:500]}...

Extract:
1. Main materials studied
2. Key finding (1 sentence)
3. Relevance to battery technology (1-10 score)

Keep response under 100 words."""

        analysis = groq.generate_text(prompt, max_tokens=200)
        print(f"\n✅ GROQ Analysis:\n{analysis}")

except Exception as e:
    print(f"❌ Analysis failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed! System is fully functional.")
print(f"\nGemini Key loaded: {settings._gemini_api_key[:20]}...")
print(f"GROQ Key loaded: {settings._groq_api_key[:20]}...")
