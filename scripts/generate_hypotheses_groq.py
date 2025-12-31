"""
Generate hypotheses using GROQ only (no Gemini refinement)

Usage: python scripts/generate_hypotheses_groq.py --per-gap 3 --max-total 30
"""

from src.utils.logger import setup_logger
from src.config.settings import Settings
from src.api.materials_project_client import MaterialsProjectClient
from src.api.groq_client import GROQClient
from src.api.gemini_client import GeminiClient
from src.reasoning.feasibility_analyzer import FeasibilityAnalyzer
from src.reasoning.novelty_checker import NoveltyChecker
from src.reasoning.hypothesis_generator import HypothesisGenerator
import sys
import os
import argparse
import json
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


logger = setup_logger()


def load_research_gaps(input_path: str) -> tuple[list, pd.DataFrame]:
    """Load research gaps from Phase 2 output"""
    logger.info(f"Loading data from {input_path}")

    # Load from JSON analysis results
    with open(input_path, 'r') as f:
        data = json.load(f)

    # Extract gaps and papers
    gaps = []
    papers_data = []

    for item in data:
        paper = item.get('paper', {})
        analysis = item.get('analysis', {})

        # Add to papers dataframe
        papers_data.append({
            'title': paper.get('title', ''),
            'abstract': paper.get('title', ''),
            'arxiv_id': paper.get('arxiv_id', ''),
            'relevance_score': analysis.get('relevance_score', 5)
        })

        # Extract gaps
        potential_gaps = analysis.get('potential_gaps', [])
        for gap in potential_gaps:
            gaps.append({
                'description': gap,
                'domain': 'battery materials',
                'score': analysis.get('relevance_score', 5),
                'source_paper': paper.get('title', ''),
                'context': analysis.get('key_finding', '')
            })

    papers_df = pd.DataFrame(papers_data)
    logger.info(
        f"Loaded {len(gaps)} research gaps from {len(papers_df)} papers")
    return gaps, papers_df


def main():
    parser = argparse.ArgumentParser(
        description="Generate hypotheses using GROQ (Gemini-free)")
    parser.add_argument('--input', default='data/results/groq_analysis_20251231_082327.json',
                        help='Path to analyzed papers JSON')
    parser.add_argument('--output', default='data/hypotheses_groq.csv',
                        help='Output path for hypotheses')
    parser.add_argument('--per-gap', type=int, default=2,
                        help='Hypotheses per research gap')
    parser.add_argument('--max-total', type=int, default=30,
                        help='Maximum total hypotheses')
    args = parser.parse_args()

    print("=" * 70)
    print("🧬 PHASE 3: HYPOTHESIS GENERATION (GROQ-ONLY MODE)")
    print("=" * 70)

    # Initialize settings
    settings = Settings()

    # Initialize API clients (skip Gemini)
    print("\n🔧 Initializing AI systems...")
    try:
        groq = GROQClient(api_key=settings.groq_api_key)
        mp = MaterialsProjectClient(api_key=settings.mp_api_key)
        print("✅ GROQ and Materials Project clients ready")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        print(f"❌ Initialization failed: {e}")
        return 1

    # Load research gaps from Phase 2
    print(f"\n📖 Loading research gaps from {args.input}...")
    try:
        gaps, papers_df = load_research_gaps(args.input)
        print(
            f"✅ Found {len(gaps)} research gaps from {len(papers_df)} papers")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        print(f"❌ Failed to load data: {e}")
        return 1

    # Print top gaps
    print("\n📊 Top 5 Research Gaps:")
    sorted_gaps = sorted(gaps, key=lambda x: x.get('score', 0), reverse=True)
    for i, gap in enumerate(sorted_gaps[:5], 1):
        score = gap.get('score', 0)
        desc = gap.get('description', '')[:80]
        print(f"  {i}. {desc}... (Score: {score:.1f}/10)")

    # Generate hypotheses (GROQ-only, skip Gemini refinement)
    print(
        f"\n💡 Generating hypotheses with GROQ ({args.per_gap} per gap, max {args.max_total})...")

    all_hypotheses = []

    for i, gap in enumerate(sorted_gaps, 1):
        if len(all_hypotheses) >= args.max_total:
            break

        print(
            f"  [{i}/{len(sorted_gaps)}] Processing gap: {gap['description'][:60]}...")

        try:
            # Generate with GROQ
            prompt = f"""Generate {args.per_gap} specific, testable hypotheses for this research gap:

Gap: {gap['description']}
Domain: {gap.get('domain', 'materials science')}

Format each hypothesis as:
HYPOTHESIS N: If we [action], then [outcome] because [reasoning].

Make hypotheses specific (mention exact materials, conditions, values) and testable."""

            response = groq.generate_text(
                prompt=prompt, max_tokens=600, temperature=0.7)

            # Parse hypotheses
            lines = response.split('\n')
            current = []

            for line in lines:
                if line.strip().startswith('HYPOTHESIS'):
                    if current:
                        hyp_text = ' '.join(current)
                        if len(hyp_text) > 50:
                            all_hypotheses.append({
                                'hypothesis': hyp_text,
                                'source_gap': gap['description'],
                                'gap_score': gap['score'],
                                'novelty_estimate': 0.7,
                                'reasoning': '',
                                'predicted_outcome': '',
                                'testable_metric': ''
                            })
                    current = [line.split(':', 1)[1].strip()
                               if ':' in line else line]
                elif current and line.strip():
                    current.append(line.strip())

            if current:
                hyp_text = ' '.join(current)
                if len(hyp_text) > 50:
                    all_hypotheses.append({
                        'hypothesis': hyp_text,
                        'source_gap': gap['description'],
                        'gap_score': gap['score'],
                        'novelty_estimate': 0.7,
                        'reasoning': '',
                        'predicted_outcome': '',
                        'testable_metric': ''
                    })

        except Exception as e:
            logger.error(f"Failed to generate for gap {i}: {e}")
            continue

    hypotheses_df = pd.DataFrame(all_hypotheses)
    print(f"✅ Generated {len(hypotheses_df)} hypotheses")

    # Check novelty
    print("\n🔍 Checking novelty...")
    try:
        novelty_checker = NoveltyChecker(papers_df)
        hypotheses_df = novelty_checker.batch_check(hypotheses_df)
        novel_count = hypotheses_df['is_novel'].sum()
        print(
            f"✅ Novel: {novel_count}/{len(hypotheses_df)} ({novel_count/len(hypotheses_df)*100:.1f}%)")
    except Exception as e:
        logger.error(f"Novelty check failed: {e}")
        print(f"⚠️ Novelty check skipped: {e}")

    # Analyze feasibility
    print("\n⚙️ Analyzing feasibility...")
    try:
        feasibility_analyzer = FeasibilityAnalyzer(mp)
        hypotheses_df = feasibility_analyzer.batch_analyze(hypotheses_df)
        feasible_count = (hypotheses_df['feasibility_level'].isin(
            ['Easy', 'Medium'])).sum()
        print(
            f"✅ Feasible: {feasible_count}/{len(hypotheses_df)} ({feasible_count/len(hypotheses_df)*100:.1f}%)")
    except Exception as e:
        logger.error(f"Feasibility check failed: {e}")
        print(f"⚠️ Feasibility check skipped: {e}")

    # Calculate priority
    print("\n📈 Calculating priority scores...")
    hypotheses_df['priority_score'] = (
        0.5 * hypotheses_df.get('novelty_score', 0.7) +
        0.5 * hypotheses_df.get('feasibility_score', 0.5)
    )

    hypotheses_df = hypotheses_df.sort_values(
        'priority_score', ascending=False)

    # Save results
    print(f"\n💾 Saving to {args.output}...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    hypotheses_df.to_csv(output_path, index=False)

    # Print top hypotheses
    print("\n" + "=" * 70)
    print("🏆 TOP 5 HYPOTHESES")
    print("=" * 70)

    for i, (_, row) in enumerate(hypotheses_df.head(5).iterrows(), 1):
        print(f"\n{i}. {row['hypothesis'][:180]}...")
        print(f"   📊 Priority: {row['priority_score']:.2f}")
        print(f"   ✨ Novelty: {row.get('novelty_score', 0):.2f}")
        print(
            f"   ⚙️ Feasibility: {row.get('feasibility_score', 0):.2f} ({row.get('feasibility_level', 'Unknown')})")

    # Statistics
    print("\n" + "=" * 70)
    print("📊 PHASE 3 STATISTICS")
    print("=" * 70)
    print(f"Total Hypotheses: {len(hypotheses_df)}")
    print(
        f"Novel Hypotheses: {hypotheses_df.get('is_novel', pd.Series([False])).sum()}")
    print(
        f"High Priority (>0.7): {(hypotheses_df['priority_score'] > 0.7).sum()}")
    print(
        f"Feasible (Easy/Medium): {(hypotheses_df.get('feasibility_level', pd.Series([])).isin(['Easy', 'Medium'])).sum()}")

    if 'novelty_score' in hypotheses_df.columns:
        print(f"Avg Novelty: {hypotheses_df['novelty_score'].mean():.2f}")
    if 'feasibility_score' in hypotheses_df.columns:
        print(
            f"Avg Feasibility: {hypotheses_df['feasibility_score'].mean():.2f}")

    print("\n🎉 PHASE 3 COMPLETE (GROQ-ONLY MODE)!")
    print(f"📁 Results: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
