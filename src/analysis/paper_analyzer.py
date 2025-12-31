"""
AI-Powered Paper Analyzer for Autonomous Scientific Agent.

This module analyzes scientific papers using AI (Gemini + GROQ) to extract
insights, identify key findings, and assess research significance.
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
from loguru import logger
from functools import wraps

from ..api.gemini_client import GeminiClient
from ..api.groq_client import GROQClient
from ..data_collection.paper_collector import Paper


def retry_on_error(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator to retry function on failure with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    last_exception = e
                    if retries < max_retries:
                        wait_time = backoff_factor ** retries
                        logger.warning(
                            f"Attempt {retries}/{max_retries} failed: {e}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        return wrapper
    return decorator


@dataclass
class PaperAnalysis:
    """Results from analyzing a scientific paper."""

    arxiv_id: str
    title: str

    # Entity extraction (from GROQ)
    materials: List[str]
    properties: List[str]
    methods: List[str]
    applications: List[str]
    performance_metrics: List[str]

    # Deep analysis (from Gemini)
    key_findings: List[str]
    research_significance: str
    novelty_assessment: str
    limitations: List[str]
    future_directions: List[str]

    # Classification
    research_type: str  # "experimental", "theoretical", "computational", "review"
    maturity_level: str  # "fundamental", "applied", "proof-of-concept", "optimization"

    # Relevance scoring
    relevance_score: float  # 0-10 scale
    confidence_score: float  # 0-1 scale

    # Metadata
    analysis_timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaperAnalysis':
        """Create from dictionary."""
        return cls(**data)


class PaperAnalyzer:
    """
    Analyze scientific papers using dual AI system.

    Uses GROQ (fast) for entity extraction and classification,
    and Gemini (powerful) for deep analysis and insights.
    """

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        groq_client: Optional[GROQClient] = None,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize paper analyzer.

        Args:
            gemini_client: Gemini client instance (creates new if None)
            groq_client: GROQ client instance (creates new if None)
            cache_dir: Directory to cache analysis results
        """
        from ..config.settings import Settings

        if gemini_client is None:
            settings = Settings()
            self.gemini = GeminiClient(api_key=settings.gemini_api_key)
        else:
            self.gemini = gemini_client

        if groq_client is None:
            settings = Settings() if gemini_client is not None else settings
            self.groq = GROQClient(api_key=settings.groq_api_key)
        else:
            self.groq = groq_client

        if cache_dir is None:
            cache_dir = Path(__file__).resolve(
            ).parents[2] / "data" / "analysis"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Initialized PaperAnalyzer with Gemini + GROQ")

    def analyze_paper(
        self,
        paper: Paper,
        focus_areas: Optional[List[str]] = None,
        skip_cache: bool = False
    ) -> PaperAnalysis:
        """
        Perform complete analysis of a paper.

        Args:
            paper: Paper object to analyze
            focus_areas: Specific areas to focus on (e.g., ["materials", "performance"])
            skip_cache: Skip cache and perform fresh analysis

        Returns:
            PaperAnalysis object with complete results
        """
        # Check cache first
        cache_file = self.cache_dir / \
            f"{paper.arxiv_id.replace('/', '_')}.json"
        if not skip_cache and cache_file.exists():
            logger.info(f"Loading cached analysis for {paper.arxiv_id}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return PaperAnalysis.from_dict(data)

        logger.info(f"Analyzing paper: {paper.title}")

        try:
            # Step 1: Fast entity extraction with GROQ (with retry)
            logger.debug("Step 1: Extracting entities (GROQ)")
            entities = self._extract_entities_with_retry(paper)

            # Step 2: Classification with GROQ (with retry)
            logger.debug("Step 2: Classifying paper (GROQ)")
            research_type, maturity_level = self._classify_paper_with_retry(paper)

            # Step 3: Deep analysis with Gemini (with retry)
            logger.debug("Step 3: Deep analysis (Gemini)")
            deep_analysis = self._deep_analyze_with_retry(paper, entities, focus_areas)

            # Step 4: Relevance scoring
            logger.debug("Step 4: Scoring relevance")
            relevance_score, confidence = self._score_relevance(
                paper, deep_analysis)

            # Combine results
            analysis = PaperAnalysis(
                arxiv_id=paper.arxiv_id,
                title=paper.title,
                materials=entities.get("materials", []),
                properties=entities.get("properties", []),
                methods=entities.get("methods", []),
                applications=entities.get("applications", []),
                performance_metrics=entities.get("performance_metrics", []),
                key_findings=deep_analysis["key_findings"],
                research_significance=deep_analysis["significance"],
                novelty_assessment=deep_analysis["novelty"],
                limitations=deep_analysis["limitations"],
                future_directions=deep_analysis["future_directions"],
                research_type=research_type,
                maturity_level=maturity_level,
                relevance_score=relevance_score,
                confidence_score=confidence,
                analysis_timestamp=pd.Timestamp.now().isoformat()
            )

            # Validate analysis quality
            if not self._validate_analysis(analysis):
                logger.warning(f"Analysis validation failed for {paper.arxiv_id}")
                raise ValueError("Analysis quality check failed - insufficient data extracted")

            # Cache results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(
                f"✅ Analysis complete (relevance: {relevance_score:.1f}/10)")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze paper {paper.arxiv_id}: {e}")
            # Return minimal analysis with error flag
            return self._create_failed_analysis(paper, str(e))

    def _validate_analysis(self, analysis: PaperAnalysis) -> bool:
        """Validate that analysis has sufficient quality data."""
        # Check that key findings are not empty
        if not analysis.key_findings or len(analysis.key_findings) == 0:
            return False
        
        # Check that at least some entities were extracted
        total_entities = (
            len(analysis.materials) + 
            len(analysis.properties) + 
            len(analysis.methods)
        )
        if total_entities == 0:
            return False
        
        # Check that relevance score is reasonable
        if analysis.relevance_score <= 0 or analysis.relevance_score > 10:
            return False
        
        return True

    def _create_failed_analysis(self, paper: Paper, error_msg: str) -> PaperAnalysis:
        """Create a minimal analysis object for failed papers."""
        return PaperAnalysis(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            materials=[],
            properties=[],
            methods=[],
            applications=[],
            performance_metrics=[],
            key_findings=["Analysis failed"],
            research_significance=f"Analysis failed: {error_msg}",
            novelty_assessment="Unknown",
            limitations=["Analysis failed"],
            future_directions=["Analysis failed"],
            research_type="unknown",
            maturity_level="unknown",
            relevance_score=0.0,
            confidence_score=0.0,
            analysis_timestamp=pd.Timestamp.now().isoformat()
        )

    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def _extract_entities_with_retry(self, paper: Paper) -> Dict[str, List[str]]:
        """Extract entities with retry logic."""
        return self._extract_entities(paper)

    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def _classify_paper_with_retry(self, paper: Paper) -> Tuple[str, str]:
        """Classify paper with retry logic."""
        return self._classify_paper(paper)

    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def _deep_analyze_with_retry(
        self,
        paper: Paper,
        entities: Dict[str, List[str]],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Deep analyze with retry logic."""
        return self._deep_analyze(paper, entities, focus_areas)

        # Combine results
        analysis = PaperAnalysis(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            materials=entities.get("materials", []),
            properties=entities.get("properties", []),
            methods=entities.get("methods", []),
            applications=entities.get("applications", []),
            performance_metrics=entities.get("performance_metrics", []),
            key_findings=deep_analysis["key_findings"],
            research_significance=deep_analysis["significance"],
            novelty_assessment=deep_analysis["novelty"],
            limitations=deep_analysis["limitations"],
            future_directions=deep_analysis["future_directions"],
            research_type=research_type,
            maturity_level=maturity_level,
            relevance_score=relevance_score,
            confidence_score=confidence,
            analysis_timestamp=pd.Timestamp.now().isoformat()
        )

        # Cache results
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(
            f"✅ Analysis complete (relevance: {relevance_score:.1f}/10)")
        return analysis

    def _extract_entities(self, paper: Paper) -> Dict[str, List[str]]:
        """Extract entities from paper using GROQ."""
        text = f"Title: {paper.title}\n\nAbstract: {paper.abstract}"

        entities = self.groq.extract_entities(
            text=text,
            entity_types=[
                "materials",
                "properties",
                "methods",
                "applications",
                "performance_metrics"
            ]
        )

        return entities

    def _classify_paper(self, paper: Paper) -> Tuple[str, str]:
        """Classify paper by research type and maturity level."""
        text = f"Title: {paper.title}\n\nAbstract: {paper.abstract}"

        # Classify research type
        research_types = [
            "experimental",
            "theoretical",
            "computational",
            "review"
        ]
        type_result = self.groq.classify_text(
            text=text,
            categories=research_types,
            multi_label=False
        )
        research_type = type_result["categories"][0] if type_result["categories"] else "unknown"

        # Classify maturity level
        maturity_levels = [
            "fundamental",
            "applied",
            "proof-of-concept",
            "optimization"
        ]
        maturity_result = self.groq.classify_text(
            text=text,
            categories=maturity_levels,
            multi_label=False
        )
        maturity_level = maturity_result["categories"][0] if maturity_result["categories"] else "unknown"

        return research_type, maturity_level

    def _deep_analyze(
        self,
        paper: Paper,
        entities: Dict[str, List[str]],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform deep analysis using Gemini."""
        focus_text = ""
        if focus_areas:
            focus_text = f"\nPay special attention to: {', '.join(focus_areas)}"

        prompt = f"""Analyze this scientific paper in depth:{focus_text}

Title: {paper.title}

Abstract: {paper.abstract}

Extracted entities:
- Materials: {', '.join(entities.get('materials', [])[:10])}
- Properties: {', '.join(entities.get('properties', [])[:10])}
- Methods: {', '.join(entities.get('methods', [])[:10])}

Provide a comprehensive analysis in JSON format with these fields:

1. "key_findings": List of 3-5 key findings from the research (be specific and quantitative where possible)
2. "significance": 2-3 sentence assessment of the research significance and potential impact
3. "novelty": 2-3 sentence evaluation of what's novel or innovative about this work
4. "limitations": List of 2-4 limitations or challenges mentioned or implied
5. "future_directions": List of 2-4 potential future research directions based on this work

Return ONLY valid JSON, no markdown formatting.
"""

        try:
            response = self.gemini.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1500
            )

            # Parse JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            analysis = json.loads(response)

            # Validate structure
            required_keys = ["key_findings", "significance",
                             "novelty", "limitations", "future_directions"]
            for key in required_keys:
                if key not in analysis:
                    logger.warning(f"Missing key in analysis: {key}")
                    analysis[key] = [
                    ] if key != "significance" and key != "novelty" else "Not assessed"

            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            logger.debug(f"Raw response: {response}")
            return {
                "key_findings": [],
                "significance": "Analysis failed",
                "novelty": "Analysis failed",
                "limitations": [],
                "future_directions": []
            }

    def _score_relevance(
        self,
        paper: Paper,
        deep_analysis: Dict[str, Any]
    ) -> Tuple[float, float]:
        """
        Score paper relevance and confidence.

        Returns:
            Tuple of (relevance_score, confidence_score)
        """
        # Build scoring prompt
        prompt = f"""Score the relevance of this scientific paper for materials science research.

Title: {paper.title}
Categories: {', '.join(paper.categories)}

Key Findings:
{chr(10).join(f'- {f}' for f in deep_analysis.get('key_findings', []))}

Significance: {deep_analysis.get('significance', 'N/A')}

Provide scores in JSON format:
{{
    "relevance_score": <float 0-10>,
    "confidence": <float 0-1>,
    "reasoning": "<brief explanation>"
}}

Relevance criteria:
- 9-10: Groundbreaking work with major implications
- 7-8: Significant contribution, advances the field
- 5-6: Solid work, incremental progress
- 3-4: Limited scope or minor contribution
- 1-2: Tangential or very narrow focus

Return ONLY valid JSON.
"""

        try:
            response = self.groq.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=200
            )

            # Parse JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            scores = json.loads(response)

            relevance = float(scores.get("relevance_score", 5.0))
            confidence = float(scores.get("confidence", 0.5))

            # Clamp values
            relevance = max(0.0, min(10.0, relevance))
            confidence = max(0.0, min(1.0, confidence))

            return relevance, confidence

        except Exception as e:
            logger.error(f"Relevance scoring failed: {e}")
            return 5.0, 0.5  # Default to medium relevance, low confidence

    def analyze_batch(
        self,
        papers: List[Paper],
        max_papers: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> List[PaperAnalysis]:
        """
        Analyze multiple papers in batch.

        Args:
            papers: List of papers to analyze
            max_papers: Maximum number to analyze (None = all)
            progress_callback: Function to call with progress updates

        Returns:
            List of PaperAnalysis objects
        """
        if max_papers:
            papers = papers[:max_papers]

        analyses = []
        total = len(papers)

        logger.info(f"Starting batch analysis of {total} papers...")

        for i, paper in enumerate(papers, 1):
            try:
                analysis = self.analyze_paper(paper)
                analyses.append(analysis)

                if progress_callback:
                    progress_callback(i, total, analysis)

                logger.info(f"Progress: {i}/{total} papers analyzed")

            except Exception as e:
                logger.error(f"Failed to analyze {paper.arxiv_id}: {e}")
                continue

        logger.info(
            f"✅ Batch analysis complete: {len(analyses)}/{total} successful")
        return analyses

    def get_analysis_dataframe(
        self,
        analyses: List[PaperAnalysis]
    ) -> pd.DataFrame:
        """
        Convert analyses to DataFrame for exploration.

        Args:
            analyses: List of PaperAnalysis objects

        Returns:
            DataFrame with analysis results
        """
        data = []
        for analysis in analyses:
            row = {
                'arxiv_id': analysis.arxiv_id,
                'title': analysis.title,
                'research_type': analysis.research_type,
                'maturity_level': analysis.maturity_level,
                'relevance_score': analysis.relevance_score,
                'confidence_score': analysis.confidence_score,
                'num_materials': len(analysis.materials),
                'num_properties': len(analysis.properties),
                'num_methods': len(analysis.methods),
                'num_findings': len(analysis.key_findings),
                'materials': ', '.join(analysis.materials[:5]),
                'properties': ', '.join(analysis.properties[:5]),
                'significance': analysis.research_significance[:200],
            }
            data.append(row)

        df = pd.DataFrame(data)
        df = df.sort_values('relevance_score', ascending=False)

        return df

    def save_analyses(
        self,
        analyses: List[PaperAnalysis],
        filename: str
    ) -> Path:
        """
        Save analyses to JSON file.

        Args:
            analyses: List of PaperAnalysis objects
            filename: Output filename (without extension)

        Returns:
            Path to saved file
        """
        filepath = self.cache_dir / f"{filename}.json"

        data = [a.to_dict() for a in analyses]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(analyses)} analyses to: {filepath}")
        return filepath

    def load_analyses(self, filename: str) -> List[PaperAnalysis]:
        """Load analyses from JSON file."""
        if not filename.endswith('.json'):
            filename += '.json'

        filepath = self.cache_dir / filename

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        analyses = [PaperAnalysis.from_dict(a) for a in data]
        logger.info(f"Loaded {len(analyses)} analyses from: {filepath}")
        return analyses


if __name__ == "__main__":
    from ..utils.logger import setup_logger
    from ..data_collection.paper_collector import ArXivCollector

    setup_logger()

    logger.info("Testing PaperAnalyzer...")

    # Get some test papers
    collector = ArXivCollector()
    papers = collector.search(
        query="graphene thermal conductivity",
        max_results=2,
        categories=["cond-mat.mtrl-sci"]
    )

    # Test analysis
    analyzer = PaperAnalyzer()

    logger.info("\n=== Test: Single Paper Analysis ===")
    analysis = analyzer.analyze_paper(papers[0])

    logger.info(f"\nTitle: {analysis.title}")
    logger.info(f"Research Type: {analysis.research_type}")
    logger.info(f"Maturity: {analysis.maturity_level}")
    logger.info(f"Relevance Score: {analysis.relevance_score}/10")
    logger.info(f"\nMaterials: {', '.join(analysis.materials)}")
    logger.info(f"Properties: {', '.join(analysis.properties)}")
    logger.info(f"\nKey Findings:")
    for finding in analysis.key_findings:
        logger.info(f"  - {finding}")
    logger.info(f"\nSignificance: {analysis.research_significance}")

    logger.info("\n✨ PaperAnalyzer test completed!")
