"""
Main Script for Paper Collection and Analysis Pipeline

This script orchestrates the complete Phase 2 workflow:
1. Collect papers from arXiv
2. Analyze papers with AI (Gemini + GROQ)
3. Extract knowledge and build knowledge graphs
4. Identify research gaps
5. Generate research hypotheses

Usage:
    python scripts/collect_and_analyze.py --query "graphene thermal conductivity" --max-papers 50
"""

from src.analysis.knowledge_extractor import KnowledgeExtractor
from src.analysis.paper_analyzer import PaperAnalyzer
from src.data_collection.paper_collector import ArXivCollector
from src.utils.logger import setup_logger
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(
        description="Autonomous Scientific Agent - Paper Collection & Analysis"
    )

    # Search parameters
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Search query for arXiv papers"
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=50,
        help="Maximum number of papers to collect (default: 50)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Search papers from last N days (default: 30)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["cond-mat.mtrl-sci", "cond-mat.mes-hall", "physics.comp-ph"],
        help="arXiv categories to search (default: materials science categories)"
    )

    # Analysis parameters
    parser.add_argument(
        "--max-analyze",
        type=int,
        default=None,
        help="Maximum number of papers to analyze (default: all collected)"
    )
    parser.add_argument(
        "--min-relevance",
        type=float,
        default=5.0,
        help="Minimum relevance score for papers (0-10, default: 5.0)"
    )

    # Knowledge extraction parameters
    parser.add_argument(
        "--min-gap-confidence",
        type=float,
        default=0.6,
        help="Minimum confidence for research gaps (0-1, default: 0.6)"
    )
    parser.add_argument(
        "--max-hypotheses",
        type=int,
        default=10,
        help="Maximum hypotheses to generate (default: 10)"
    )

    # Output parameters
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/results",
        help="Output directory for results (default: data/results)"
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default=None,
        help="Base name for output files (default: auto-generated from query)"
    )

    # Options
    parser.add_argument(
        "--skip-collection",
        action="store_true",
        help="Skip paper collection (use existing papers)"
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip paper analysis (use cached analyses)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logger(log_level=args.log_level)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output name
    if args.output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = args.query.replace(" ", "_")[:30]
        output_name = f"{query_slug}_{timestamp}"
    else:
        output_name = args.output_name

    logger.info("=" * 80)
    logger.info("AUTONOMOUS SCIENTIFIC AGENT - Phase 2 Pipeline")
    logger.info("=" * 80)
    logger.info(f"Query: {args.query}")
    logger.info(f"Max papers: {args.max_papers}")
    logger.info(f"Output: {output_dir / output_name}")
    logger.info("=" * 80)

    # ===== STEP 1: COLLECT PAPERS =====
    if not args.skip_collection:
        logger.info("\n📚 STEP 1: Collecting papers from arXiv...")
        logger.info(f"  Query: {args.query}")
        logger.info(f"  Categories: {', '.join(args.categories)}")
        logger.info(f"  Time range: Last {args.days} days")

        collector = ArXivCollector()

        papers = collector.search_recent(
            query=args.query,
            days=args.days,
            max_results=args.max_papers,
            categories=args.categories
        )

        if not papers:
            logger.error(
                "❌ No papers found! Try a different query or broader categories.")
            return 1

        logger.info(f"✅ Collected {len(papers)} papers")

        # Save papers
        papers_file = collector.save_papers(
            papers, f"{output_name}_papers", format="json")
        logger.info(f"  Saved to: {papers_file}")

        # Also save as CSV for easy viewing
        collector.save_papers(papers, f"{output_name}_papers", format="csv")

    else:
        logger.info("\n📚 STEP 1: Loading existing papers...")
        collector = ArXivCollector()
        try:
            papers = collector.load_papers(f"{output_name}_papers")
            logger.info(f"✅ Loaded {len(papers)} papers")
        except FileNotFoundError:
            logger.error(f"❌ Papers file not found: {output_name}_papers.json")
            return 1

    # ===== STEP 2: ANALYZE PAPERS =====
    if not args.skip_analysis:
        logger.info("\n🤖 STEP 2: Analyzing papers with AI...")
        logger.info(
            f"  Using: Gemini (deep analysis) + GROQ (entity extraction)")

        analyzer = PaperAnalyzer()

        # Progress callback
        def progress_callback(current, total, analysis):
            logger.info(
                f"  [{current}/{total}] {analysis.title[:50]}... "
                f"(relevance: {analysis.relevance_score:.1f}/10)"
            )

        analyses = analyzer.analyze_batch(
            papers,
            max_papers=args.max_analyze,
            progress_callback=progress_callback
        )

        if not analyses:
            logger.error("❌ No papers were successfully analyzed!")
            return 1

        logger.info(f"✅ Analyzed {len(analyses)} papers")

        # Filter by relevance
        high_relevance = [
            a for a in analyses if a.relevance_score >= args.min_relevance]
        logger.info(
            f"  {len(high_relevance)} papers meet relevance threshold (≥{args.min_relevance})")

        # Save analyses
        analyses_file = analyzer.save_analyses(
            analyses, f"{output_name}_analyses")
        logger.info(f"  Saved to: {analyses_file}")

        # Save summary DataFrame
        df = analyzer.get_analysis_dataframe(analyses)
        df_file = output_dir / f"{output_name}_summary.csv"
        df.to_csv(df_file, index=False)
        logger.info(f"  Summary saved to: {df_file}")

    else:
        logger.info("\n🤖 STEP 2: Loading existing analyses...")
        analyzer = PaperAnalyzer()
        try:
            analyses = analyzer.load_analyses(f"{output_name}_analyses")
            high_relevance = [
                a for a in analyses if a.relevance_score >= args.min_relevance]
            logger.info(
                f"✅ Loaded {len(analyses)} analyses ({len(high_relevance)} high-relevance)")
        except FileNotFoundError:
            logger.error(
                f"❌ Analyses file not found: {output_name}_analyses.json")
            return 1

    # ===== STEP 3: EXTRACT KNOWLEDGE =====
    logger.info("\n🧠 STEP 3: Building knowledge graph...")

    extractor = KnowledgeExtractor()
    graph = extractor.build_knowledge_graph(analyses)

    # Get graph statistics
    stats = extractor.get_graph_statistics()
    logger.info(f"  Nodes: {stats['total_nodes']} ({stats['num_materials']} materials, "
                f"{stats['num_properties']} properties, {stats['num_methods']} methods)")
    logger.info(f"  Edges: {stats['total_edges']}")

    # Save knowledge graph
    graph_file = extractor.save_knowledge_graph(
        f"{output_name}_knowledge_graph")
    logger.info(f"  Saved to: {graph_file}")

    # Find patterns
    logger.info("\n🔍 Finding research patterns...")
    patterns = extractor.find_frequent_patterns(min_frequency=2)

    logger.info(f"\nTop Materials:")
    for material, freq in patterns["top_materials"][:5]:
        logger.info(f"  • {material} (mentioned {freq}x)")

    logger.info(f"\nTop Properties:")
    for prop, freq in patterns["top_properties"][:5]:
        logger.info(f"  • {prop} (mentioned {freq}x)")

    logger.info(f"\nFrequent Material-Property Pairs:")
    for pair, freq in patterns["material_property_pairs"][:5]:
        logger.info(f"  • {pair} (co-occur {freq}x)")

    # Save patterns
    patterns_file = output_dir / f"{output_name}_patterns.json"
    with open(patterns_file, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, indent=2, ensure_ascii=False)
    logger.info(f"\n  Patterns saved to: {patterns_file}")

    # ===== STEP 4: IDENTIFY GAPS =====
    logger.info("\n🎯 STEP 4: Identifying research gaps...")

    gaps = extractor.identify_research_gaps(
        analyses,
        min_gap_confidence=args.min_gap_confidence
    )

    logger.info(f"✅ Identified {len(gaps)} research gaps")

    for i, gap in enumerate(gaps[:5], 1):
        logger.info(
            f"\nGap {i} [{gap.priority} priority, {gap.confidence:.0%} confidence]:")
        logger.info(f"  {gap.description[:200]}...")
        if gap.related_materials:
            logger.info(f"  Materials: {', '.join(gap.related_materials[:5])}")
        if gap.related_properties:
            logger.info(
                f"  Properties: {', '.join(gap.related_properties[:5])}")

    # Save gaps
    gaps_file = output_dir / f"{output_name}_gaps.json"
    with open(gaps_file, 'w', encoding='utf-8') as f:
        json.dump([g.to_dict() for g in gaps], f, indent=2, ensure_ascii=False)
    logger.info(f"\n  Gaps saved to: {gaps_file}")

    # ===== STEP 5: GENERATE HYPOTHESES =====
    logger.info("\n💡 STEP 5: Generating research hypotheses...")

    hypotheses = extractor.generate_hypotheses(
        gaps,
        analyses,
        max_hypotheses=args.max_hypotheses
    )

    logger.info(f"✅ Generated {len(hypotheses)} hypotheses")

    for i, hyp in enumerate(hypotheses, 1):
        logger.info(f"\nHypothesis {i} [{hyp.feasibility} feasibility, "
                    f"novelty: {hyp.novelty_score:.1f}/10]:")
        logger.info(f"  Statement: {hyp.statement}")
        logger.info(f"  Rationale: {hyp.rationale[:150]}...")
        if hyp.materials_involved:
            logger.info(
                f"  Materials: {', '.join(hyp.materials_involved[:3])}")
        if hyp.suggested_methods:
            logger.info(f"  Methods: {', '.join(hyp.suggested_methods[:3])}")

    # Save hypotheses
    hyp_file = output_dir / f"{output_name}_hypotheses.json"
    with open(hyp_file, 'w', encoding='utf-8') as f:
        json.dump([h.to_dict() for h in hypotheses],
                  f, indent=2, ensure_ascii=False)
    logger.info(f"\n  Hypotheses saved to: {hyp_file}")

    # ===== SUMMARY =====
    logger.info("\n" + "=" * 80)
    logger.info("✨ PIPELINE COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Papers collected: {len(papers)}")
    logger.info(f"Papers analyzed: {len(analyses)}")
    logger.info(f"High-relevance papers: {len(high_relevance)}")
    logger.info(
        f"Knowledge graph: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
    logger.info(f"Research gaps: {len(gaps)}")
    logger.info(f"Hypotheses: {len(hypotheses)}")
    logger.info(f"\nAll results saved to: {output_dir}")
    logger.info("=" * 80)

    # Create summary report
    summary = {
        "query": args.query,
        "timestamp": datetime.now().isoformat(),
        "parameters": vars(args),
        "results": {
            "papers_collected": len(papers),
            "papers_analyzed": len(analyses),
            "high_relevance_papers": len(high_relevance),
            "knowledge_graph_nodes": stats['total_nodes'],
            "knowledge_graph_edges": stats['total_edges'],
            "research_gaps": len(gaps),
            "hypotheses": len(hypotheses)
        },
        "files": {
            "papers": str(papers_file) if not args.skip_collection else "N/A",
            "analyses": str(analyses_file) if not args.skip_analysis else "N/A",
            "summary_csv": str(df_file) if not args.skip_analysis else "N/A",
            "knowledge_graph": str(graph_file),
            "patterns": str(patterns_file),
            "gaps": str(gaps_file),
            "hypotheses": str(hyp_file)
        }
    }

    summary_file = output_dir / f"{output_name}_SUMMARY.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logger.info(f"\n📊 Pipeline summary: {summary_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
