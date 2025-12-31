"""
Autonomous Scientific Agent
Runs complete research loop: collect → analyze → hypothesize → test → iterate
"""

import time
import pandas as pd
import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from ..data_collection.paper_collector import ArXivCollector
from ..analysis.paper_analyzer import PaperAnalyzer
from ..reasoning.hypothesis_generator import HypothesisGenerator
from ..reasoning.novelty_checker import NoveltyChecker
from ..reasoning.feasibility_analyzer import FeasibilityAnalyzer
from ..experiments.hypothesis_tester import HypothesisTester

from ..api.gemini_client import GeminiClient
from ..api.groq_client import GROQClient
from ..api.materials_project_client import MaterialsProjectClient
from ..config.settings import Settings
from ..utils.logger import setup_logger

logger = setup_logger()


class AutonomousScientist:
    """
    Fully autonomous scientific research agent
    """

    def __init__(self, domain: str = "materials science"):
        """
        Initialize autonomous agent

        Args:
            domain: Research domain
        """
        self.domain = domain
        self.iteration = 0
        self.discoveries = []

        # Initialize API clients
        logger.info("Initializing AI systems...")
        try:
            settings = Settings()
            self.gemini = GeminiClient(api_key=settings.gemini_api_key)
            self.groq = GROQClient(api_key=settings.groq_api_key)
            self.mp = MaterialsProjectClient(api_key=settings.mp_api_key)
        except Exception as e:
            logger.warning(f"Some API clients failed to initialize: {e}")
            # Try to initialize what we can
            try:
                settings = Settings()
                self.groq = GROQClient(api_key=settings.groq_api_key)
                self.mp = MaterialsProjectClient(api_key=settings.mp_api_key)
                self.gemini = None
                logger.info("Running in GROQ-only mode")
            except Exception as e2:
                raise RuntimeError(
                    f"Failed to initialize required API clients: {e2}")

        # Initialize components
        self.collector = ArXivCollector()
        self.analyzer = PaperAnalyzer(
            self.gemini, self.groq) if self.gemini else None
        self.generator = HypothesisGenerator(
            self.gemini, self.groq) if self.gemini else None
        self.tester = HypothesisTester(self.mp, self.groq)

        # State
        self.papers = pd.DataFrame()
        self.gaps = []
        self.hypotheses = pd.DataFrame()
        self.test_results = pd.DataFrame()

        logger.success("Autonomous agent initialized")

    def run(
        self,
        query: str,
        max_papers: int = 20,
        max_hypotheses: int = 20,
        max_iterations: int = 1
    ) -> Dict:
        """
        Run autonomous research cycle

        Args:
            query: Research query
            max_papers: Papers to collect
            max_hypotheses: Hypotheses to generate
            max_iterations: Max research cycles

        Returns:
            Summary dict with all results
        """
        logger.info(f"🚀 Starting autonomous research on: {query}")

        for iteration in range(max_iterations):
            self.iteration = iteration + 1
            logger.info(f"\n{'='*60}")
            logger.info(f"ITERATION {self.iteration}/{max_iterations}")
            logger.info(f"{'='*60}\n")

            # Phase 1: Collect papers
            logger.info("📚 Phase 1: Collecting papers...")
            self.papers = self._collect_papers(query, max_papers)
            logger.success(f"Collected {len(self.papers)} papers")

            # Phase 2: Analyze papers (if available)
            if self.analyzer:
                logger.info("\n🤖 Phase 2: Analyzing papers...")
                self.papers = self._analyze_papers(self.papers)
                self.gaps = self._extract_gaps(self.papers)
                logger.success(f"Found {len(self.gaps)} research gaps")

            # Phase 3: Generate hypotheses (if available)
            if self.generator and self.gaps:
                logger.info("\n💡 Phase 3: Generating hypotheses...")
                self.hypotheses = self._generate_hypotheses(
                    self.gaps, max_hypotheses)
                logger.success(f"Generated {len(self.hypotheses)} hypotheses")

            # Phase 4: Test hypotheses
            if len(self.hypotheses) > 0:
                logger.info("\n🧪 Phase 4: Testing hypotheses...")
                self.test_results = self._test_hypotheses(self.hypotheses)
                logger.success(f"Tested {len(self.test_results)} hypotheses")

            # Phase 5: Evaluate results
            logger.info("\n📊 Phase 5: Evaluating results...")
            discoveries = self._evaluate_results(self.test_results)

            if discoveries:
                logger.success(
                    f"🎉 Found {len(discoveries)} promising discoveries!")
                self.discoveries.extend(discoveries)

        # Generate final report
        summary = self._generate_summary()

        logger.success(f"\n🎉 Autonomous research complete!")
        logger.info(f"Total discoveries: {len(self.discoveries)}")

        return summary

    def _collect_papers(self, query: str, max_papers: int) -> pd.DataFrame:
        """Collect papers from arXiv"""
        try:
            papers = self.collector.search(query, max_results=max_papers)
            return pd.DataFrame(papers) if papers else pd.DataFrame()
        except Exception as e:
            logger.error(f"Paper collection failed: {e}")
            return pd.DataFrame()

    def _analyze_papers(self, papers: pd.DataFrame) -> pd.DataFrame:
        """Analyze papers with AI"""
        if papers.empty or not self.analyzer:
            return papers

        try:
            # Convert to list of dicts for analyzer
            papers_list = papers.to_dict('records')
            analyzed = []

            # Limit to avoid quota
            for paper in papers_list[:min(10, len(papers_list))]:
                try:
                    result = self.analyzer.analyze_paper(paper)
                    analyzed.append(result)
                    time.sleep(1)
                except Exception as e:
                    logger.debug(f"Failed to analyze paper: {e}")
                    analyzed.append(paper)

            return pd.DataFrame(analyzed) if analyzed else papers
        except Exception as e:
            logger.error(f"Paper analysis failed: {e}")
            return papers

    def _extract_gaps(self, papers: pd.DataFrame) -> List[Dict]:
        """Extract research gaps"""
        gaps = []
        if papers.empty:
            return gaps

        for idx, row in papers.iterrows():
            gap_field = row.get('research_gap') or row.get('potential_gaps')
            if pd.notna(gap_field):
                if isinstance(gap_field, list):
                    for gap in gap_field:
                        gaps.append({
                            'description': gap,
                            'score': row.get('relevance_score', 5.0),
                            'source': row.get('title', '')
                        })
                else:
                    gaps.append({
                        'description': str(gap_field),
                        'score': row.get('relevance_score', 5.0),
                        'source': row.get('title', '')
                    })

        return sorted(gaps, key=lambda x: x.get('score', 0), reverse=True)

    def _generate_hypotheses(self, gaps: List[Dict], max_count: int) -> pd.DataFrame:
        """Generate hypotheses from gaps"""
        if not gaps or not self.generator:
            return pd.DataFrame()

        try:
            hypotheses = self.generator.generate_from_all_gaps(
                gaps, hypotheses_per_gap=2, max_total=max_count
            )

            if hypotheses.empty:
                return hypotheses

            # Check novelty
            if not self.papers.empty:
                try:
                    checker = NoveltyChecker(self.papers)
                    hypotheses = checker.batch_check(hypotheses)
                except Exception as e:
                    logger.debug(f"Novelty check failed: {e}")

            # Check feasibility
            try:
                feasibility = FeasibilityAnalyzer(self.mp)
                hypotheses = feasibility.batch_analyze(hypotheses)
            except Exception as e:
                logger.debug(f"Feasibility check failed: {e}")

            return hypotheses
        except Exception as e:
            logger.error(f"Hypothesis generation failed: {e}")
            return pd.DataFrame()

    def _test_hypotheses(self, hypotheses: pd.DataFrame) -> pd.DataFrame:
        """Test hypotheses computationally"""
        if hypotheses.empty:
            return hypotheses

        try:
            # Test top 10 most promising
            if 'priority_score' in hypotheses.columns:
                top_hypotheses = hypotheses.nlargest(10, 'priority_score')
            else:
                top_hypotheses = hypotheses.head(10)

            tested = self.tester.batch_test(top_hypotheses, max_tests=10)
            return tested
        except Exception as e:
            logger.error(f"Hypothesis testing failed: {e}")
            return hypotheses

    def _evaluate_results(self, test_results: pd.DataFrame) -> List[Dict]:
        """Evaluate test results for discoveries"""
        discoveries = []

        if test_results.empty:
            return discoveries

        for idx, row in test_results.iterrows():
            if row.get('test_result') == 'PASS' and row.get('test_confidence', 0) > 0.6:
                discoveries.append({
                    'hypothesis': row.get('hypothesis', ''),
                    'confidence': row.get('test_confidence', 0),
                    'evidence': str(row.get('test_evidence', {}))[:200],
                    'iteration': self.iteration
                })

        return discoveries

    def _generate_summary(self) -> Dict:
        """Generate final summary"""
        return {
            'domain': self.domain,
            'iterations': self.iteration,
            'papers_collected': len(self.papers),
            'gaps_identified': len(self.gaps),
            'hypotheses_generated': len(self.hypotheses),
            'hypotheses_tested': len(self.test_results),
            'discoveries': len(self.discoveries),
            'timestamp': datetime.now().isoformat()
        }

    def save_results(self, output_dir: str = "data/agent_results"):
        """Save all results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if not self.papers.empty:
            self.papers.to_csv(output_path / "papers.csv", index=False)

        if not self.hypotheses.empty:
            self.hypotheses.to_csv(output_path / "hypotheses.csv", index=False)

        if not self.test_results.empty:
            self.test_results.to_csv(
                output_path / "test_results.csv", index=False)

        # Save discoveries
        with open(output_path / "discoveries.json", 'w') as f:
            json.dump(self.discoveries, f, indent=2)

        # Save summary
        summary = self._generate_summary()
        with open(output_path / "summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

        logger.success(f"Results saved to {output_dir}/")
