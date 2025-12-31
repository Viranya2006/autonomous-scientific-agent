"""
Run paper collection and analysis using GROQ only (bypassing Gemini quota issues)
"""
from loguru import logger
from src.utils.logger import setup_logger
from src.data_collection.paper_collector import ArXivCollector
from src.api.groq_client import GROQClient
from src.config.settings import Settings
import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


setup_logger(log_level="INFO")


def main():
    # Initialize
    settings = Settings()

    # Force use the correct API key from .env
    print(f"\n📋 Using API keys from: {settings._env_file_path}")
    print(f"   Gemini: {settings._gemini_api_key[:25]}...")
    print(f"   GROQ: {settings._groq_api_key[:25]}...\n")

    groq = GROQClient(api_key=settings.groq_api_key)
    collector = ArXivCollector()

    # Collect papers
    query = "battery materials energy storage"
    max_papers = 20

    logger.info(f"📚 Collecting {max_papers} papers on '{query}'...")
    papers = collector.search(
        query=query,
        max_results=max_papers,
        categories=["cond-mat.mtrl-sci", "physics.chem-ph"]
    )

    logger.info(f"✅ Collected {len(papers)} papers")

    if not papers:
        logger.error("❌ No papers collected!")
        return

    # Analyze papers with GROQ
    results = []
    logger.info(f"\n🤖 Analyzing papers with GROQ...")

    for i, paper in enumerate(papers, 1):
        try:
            logger.info(f"  [{i}/{len(papers)}] {paper.title[:60]}...")

            prompt = f"""Analyze this battery/energy storage research paper:

Title: {paper.title}
Abstract: {paper.abstract[:800]}

Extract in JSON format:
{{
  "materials": ["list key materials"],
  "key_finding": "one sentence summary",
  "relevance_score": 1-10,
  "research_type": "experimental/computational/review",
  "potential_gaps": ["potential research gaps mentioned"]
}}"""

            analysis_text = groq.generate_text(prompt, max_tokens=300)

            # Try to parse JSON response
            try:
                # Find JSON in response
                start = analysis_text.find('{')
                end = analysis_text.rfind('}') + 1
                if start >= 0 and end > start:
                    analysis_json = json.loads(analysis_text[start:end])
                else:
                    analysis_json = {"raw_response": analysis_text}
            except:
                analysis_json = {"raw_response": analysis_text}

            results.append({
                "paper": {
                    "title": paper.title,
                    "arxiv_id": paper.arxiv_id,
                    "authors": paper.authors[:3],
                    "url": paper.arxiv_url
                },
                "analysis": analysis_json
            })

        except Exception as e:
            logger.error(f"  ❌ Failed: {e}")
            continue

    # Save results
    output_dir = Path("data/results")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"groq_analysis_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n💾 Saved {len(results)} analyses to: {output_file}")

    # Summary
    print(f"\n{'='*70}")
    print("📊 ANALYSIS SUMMARY")
    print(f"{'='*70}")
    print(f"Papers collected: {len(papers)}")
    print(f"Papers analyzed: {len(results)}")

    if results:
        scores = [r['analysis'].get('relevance_score', 0) for r in results if isinstance(
            r['analysis'].get('relevance_score'), (int, float))]
        if scores:
            print(f"Average relevance: {sum(scores)/len(scores):.1f}/10")

        print(f"\n🔬 Top 3 most relevant papers:")
        sorted_results = sorted(results, key=lambda x: x['analysis'].get(
            'relevance_score', 0), reverse=True)
        for i, r in enumerate(sorted_results[:3], 1):
            paper_info = r['paper']
            analysis = r['analysis']
            print(f"\n{i}. {paper_info['title'][:70]}...")
            print(f"   ArXiv: {paper_info['arxiv_id']}")
            print(f"   Score: {analysis.get('relevance_score', 'N/A')}/10")
            if 'key_finding' in analysis:
                print(f"   Finding: {analysis['key_finding'][:100]}")

    print(f"\n{'='*70}")
    print("✅ Analysis complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
