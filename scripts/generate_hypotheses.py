"""
Generate and validate hypotheses from Phase 2 research gaps

Usage: 
    python scripts/generate_hypotheses.py --input data/results/groq_analysis_20251231_082327.json --output data/hypotheses.csv
    python scripts/generate_hypotheses.py --per-gap 3 --max-total 30 --skip-validation
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
    """
    Load research gaps from Phase 2 output

    Returns:
        (gaps list, papers dataframe)
    """
    logger.info(f"Loading data from {input_path}")

    # Check file extension
    if input_path.endswith('.json'):
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
                'abstract': paper.get('title', ''),  # Use title as proxy
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

    elif input_path.endswith('.csv'):
        # Load from CSV
        df = pd.read_csv(input_path)
        papers_df = df.copy()

        # Extract gaps from CSV
        gaps = []
        for idx, row in df.iterrows():
            if pd.notna(row.get('research_gap')):
                gaps.append({
                    'description': row['research_gap'],
                    'domain': row.get('domain', 'materials science'),
                    'score': row.get('relevance_score', 5.0),
                    'source_paper': row.get('title', ''),
                    'context': row.get('key_findings', '')
                })
    else:
        raise ValueError(f"Unsupported file format: {input_path}")

    logger.info(
        f"Loaded {len(gaps)} research gaps from {len(papers_df)} papers")
    return gaps, papers_df


def main():
    parser = argparse.ArgumentParser(
        description="Generate scientific hypotheses from research gaps")
    parser.add_argument('--input', default='data/results/groq_analysis_20251231_082327.json',
                        help='Path to analyzed papers JSON or CSV')
    parser.add_argument('--output', default='data/hypotheses.csv',
                        help='Output path for hypotheses')
    parser.add_argument('--per-gap', type=int, default=3,
                        help='Hypotheses per research gap')
    parser.add_argument('--max-total', type=int, default=30,
                        help='Maximum total hypotheses')
    parser.add_argument('--skip-validation', action='store_true',
                        help='Skip novelty and feasibility checks (faster)')
    args = parser.parse_args()

    print("=" * 70)
    print("🧬 PHASE 3: HYPOTHESIS GENERATION & VALIDATION")
    print("=" * 70)

    # Initialize settings
    settings = Settings()

    # Initialize API clients
    print("\n🔧 Initializing AI systems...")
    try:
        gemini = GeminiClient(api_key=settings.gemini_api_key)
        groq = GROQClient(api_key=settings.groq_api_key)
        mp = MaterialsProjectClient(api_key=settings.mp_api_key)
        print("✅ API clients ready")
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

    # Generate hypotheses
    print(
        f"\n💡 Generating hypotheses ({args.per_gap} per gap, max {args.max_total})...")
    try:
        generator = HypothesisGenerator(gemini, groq, creativity_level=0.7)

        hypotheses_df = generator.generate_from_all_gaps(
            gaps=sorted_gaps,
            hypotheses_per_gap=args.per_gap,
            max_total=args.max_total
        )

        print(f"✅ Generated {len(hypotheses_df)} hypotheses")

    except Exception as e:
        logger.error(f"Hypothesis generation failed: {e}")
        print(f"❌ Generation failed: {e}")
        return 1

    if not args.skip_validation and len(hypotheses_df) > 0:
        # Check novelty
        print("\n🔍 Checking novelty against existing literature...")
        try:
            novelty_checker = NoveltyChecker(papers_df)
            hypotheses_df = novelty_checker.batch_check(hypotheses_df)

            novel_count = hypotheses_df['is_novel'].sum()
            total = len(hypotheses_df)
            print(
                f"✅ Novel hypotheses: {novel_count}/{total} ({novel_count/total*100:.1f}%)")
        except Exception as e:
            logger.error(f"Novelty check failed: {e}")
            print(f"⚠️ Novelty check failed: {e}")

        # Analyze feasibility
        print("\n⚙️ Analyzing computational feasibility...")
        try:
            feasibility_analyzer = FeasibilityAnalyzer(mp)
            hypotheses_df = feasibility_analyzer.batch_analyze(hypotheses_df)

            feasible_count = (hypotheses_df['feasibility_level'].isin(
                ['Easy', 'Medium'])).sum()
            total = len(hypotheses_df)
            print(
                f"✅ Feasible hypotheses: {feasible_count}/{total} ({feasible_count/total*100:.1f}%)")
        except Exception as e:
            logger.error(f"Feasibility analysis failed: {e}")
            print(f"⚠️ Feasibility analysis failed: {e}")

    # Calculate final priority scores
    print("\n📈 Calculating priority scores...")
    hypotheses_df['priority_score'] = (
        0.4 * hypotheses_df.get('novelty_score', 0.5) +
        0.3 * hypotheses_df.get('feasibility_score', 0.5) +
        0.3 * hypotheses_df.get('novelty_estimate', 0.5)
    )

    # Sort by priority
    hypotheses_df = hypotheses_df.sort_values(
        'priority_score', ascending=False)

    # Save results
    print(f"\n💾 Saving hypotheses to {args.output}...")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    hypotheses_df.to_csv(output_path, index=False)
    print(f"✅ Saved {len(hypotheses_df)} hypotheses")

    # Print top hypotheses
    print("\n" + "=" * 70)
    print("🏆 TOP 5 HYPOTHESES")
    print("=" * 70)

    for i, (idx, row) in enumerate(hypotheses_df.head(5).iterrows(), 1):
        hyp = row.get('hypothesis', '')[:200]
        priority = row.get('priority_score', 0)
        novelty = row.get('novelty_score', 0)
        feasibility = row.get('feasibility_score', 0)
        level = row.get('feasibility_level', 'Unknown')
        outcome = row.get('predicted_outcome', 'N/A')[:100]

        print(f"\n{i}. {hyp}...")
        print(f"   📊 Priority: {priority:.2f}")
        print(f"   ✨ Novelty: {novelty:.2f}")
        print(f"   ⚙️ Feasibility: {feasibility:.2f} ({level})")
        print(f"   🎯 Predicted: {outcome}")

    # Statistics
    print("\n" + "=" * 70)
    print("📊 PHASE 3 STATISTICS")
    print("=" * 70)
    print(f"Total Hypotheses Generated: {len(hypotheses_df)}")
    print(
        f"Novel Hypotheses: {hypotheses_df.get('is_novel', pd.Series([False])).sum()}")
    print(
        f"High Priority (score > 0.7): {(hypotheses_df['priority_score'] > 0.7).sum()}")
    print(
        f"Computationally Feasible: {(hypotheses_df.get('feasibility_level', pd.Series([])).isin(['Easy', 'Medium'])).sum()}")

    if 'novelty_score' in hypotheses_df.columns:
        print(
            f"Average Novelty Score: {hypotheses_df['novelty_score'].mean():.2f}")
    if 'feasibility_score' in hypotheses_df.columns:
        print(
            f"Average Feasibility Score: {hypotheses_df['feasibility_score'].mean():.2f}")

    print("\n🎉 PHASE 3 COMPLETE!")
    print(f"📁 Results saved to: {args.output}")
    print("📈 Ready for Phase 4: Autonomous Agent Loop & Experiments")
    print("\nNext steps:")
    print("  1. Review top hypotheses in", args.output)
    print("  2. Select promising candidates for computational validation")
    print("  3. Proceed to Phase 4 for automated testing")

    return 0


if __name__ == "__main__":
    sys.exit(main())
