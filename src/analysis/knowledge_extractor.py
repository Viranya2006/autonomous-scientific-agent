"""
Knowledge Extraction System for Autonomous Scientific Agent.

This module builds knowledge graphs from analyzed papers, identifies
research gaps, and generates hypothesis suggestions.
"""

import json
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict, Counter
import pandas as pd
import networkx as nx
from loguru import logger

from .paper_analyzer import PaperAnalysis
from ..api.gemini_client import GeminiClient


@dataclass
class ResearchGap:
    """Represents an identified research gap."""

    gap_id: str
    description: str
    related_materials: List[str]
    related_properties: List[str]
    supporting_evidence: List[str]  # List of arxiv_ids
    confidence: float
    priority: str  # "high", "medium", "low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Hypothesis:
    """Represents a research hypothesis."""

    hypothesis_id: str
    statement: str
    rationale: str
    related_gap: Optional[str]
    materials_involved: List[str]
    properties_involved: List[str]
    suggested_methods: List[str]
    feasibility: str  # "high", "medium", "low"
    novelty_score: float  # 0-10

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class KnowledgeExtractor:
    """
    Extract structured knowledge from analyzed papers.

    Builds knowledge graphs, identifies patterns, discovers gaps,
    and generates research hypotheses using AI.
    """

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize knowledge extractor.

        Args:
            gemini_client: Gemini client for hypothesis generation
            cache_dir: Directory to cache knowledge graphs and results
        """
        if gemini_client is None:
            from ..config.settings import Settings
            settings = Settings()
            self.gemini = GeminiClient(api_key=settings.gemini_api_key)
        else:
            self.gemini = gemini_client

        if cache_dir is None:
            cache_dir = Path(__file__).resolve(
            ).parents[2] / "data" / "knowledge"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.graph = nx.MultiDiGraph()  # Knowledge graph

        logger.info("Initialized KnowledgeExtractor")

    def build_knowledge_graph(
        self,
        analyses: List[PaperAnalysis]
    ) -> nx.MultiDiGraph:
        """
        Build knowledge graph from paper analyses.

        Nodes represent entities (materials, properties, methods)
        Edges represent relationships found in papers

        Args:
            analyses: List of PaperAnalysis objects

        Returns:
            NetworkX MultiDiGraph knowledge graph
        """
        logger.info(f"Building knowledge graph from {len(analyses)} papers...")

        self.graph.clear()

        for analysis in analyses:
            paper_id = analysis.arxiv_id

            # Add material nodes
            for material in analysis.materials:
                if not self.graph.has_node(material):
                    self.graph.add_node(
                        material,
                        type="material",
                        papers=set(),
                        frequency=0
                    )
                self.graph.nodes[material]["papers"].add(paper_id)
                self.graph.nodes[material]["frequency"] += 1

            # Add property nodes
            for prop in analysis.properties:
                if not self.graph.has_node(prop):
                    self.graph.add_node(
                        prop,
                        type="property",
                        papers=set(),
                        frequency=0
                    )
                self.graph.nodes[prop]["papers"].add(paper_id)
                self.graph.nodes[prop]["frequency"] += 1

            # Add method nodes
            for method in analysis.methods:
                if not self.graph.has_node(method):
                    self.graph.add_node(
                        method,
                        type="method",
                        papers=set(),
                        frequency=0
                    )
                self.graph.nodes[method]["papers"].add(paper_id)
                self.graph.nodes[method]["frequency"] += 1

            # Add edges: material -> property (if studied together)
            for material in analysis.materials:
                for prop in analysis.properties:
                    self.graph.add_edge(
                        material,
                        prop,
                        relation="has_property",
                        paper=paper_id,
                        relevance=analysis.relevance_score
                    )

            # Add edges: method -> material (if method used on material)
            for method in analysis.methods:
                for material in analysis.materials:
                    self.graph.add_edge(
                        method,
                        material,
                        relation="studies",
                        paper=paper_id,
                        relevance=analysis.relevance_score
                    )

        logger.info(
            f"Built graph: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )

        return self.graph

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        stats = {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "num_materials": sum(1 for n, d in self.graph.nodes(data=True) if d.get("type") == "material"),
            "num_properties": sum(1 for n, d in self.graph.nodes(data=True) if d.get("type") == "property"),
            "num_methods": sum(1 for n, d in self.graph.nodes(data=True) if d.get("type") == "method"),
        }

        # Most connected nodes
        if self.graph.number_of_nodes() > 0:
            degree_dict = dict(self.graph.degree())
            top_nodes = sorted(degree_dict.items(),
                               key=lambda x: x[1], reverse=True)[:10]
            stats["most_connected"] = [
                {"node": node, "connections": degree,
                    "type": self.graph.nodes[node].get("type")}
                for node, degree in top_nodes
            ]

        return stats

    def find_frequent_patterns(
        self,
        min_frequency: int = 3
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Find frequently occurring patterns in the knowledge graph.

        Args:
            min_frequency: Minimum frequency for a pattern to be included

        Returns:
            Dictionary of pattern types to lists of (pattern, frequency)
        """
        patterns = {
            "material_property_pairs": [],
            "material_method_pairs": [],
            "top_materials": [],
            "top_properties": [],
            "top_methods": []
        }

        # Material-property co-occurrence
        mat_prop_pairs = Counter()
        for u, v, d in self.graph.edges(data=True):
            if (self.graph.nodes[u].get("type") == "material" and
                    self.graph.nodes[v].get("type") == "property"):
                mat_prop_pairs[(u, v)] += 1

        patterns["material_property_pairs"] = [
            (f"{mat} -> {prop}", count)
            for (mat, prop), count in mat_prop_pairs.most_common(20)
            if count >= min_frequency
        ]

        # Material-method co-occurrence
        mat_method_pairs = Counter()
        for u, v, d in self.graph.edges(data=True):
            if (self.graph.nodes[u].get("type") == "method" and
                    self.graph.nodes[v].get("type") == "material"):
                mat_method_pairs[(u, v)] += 1

        patterns["material_method_pairs"] = [
            (f"{method} -> {mat}", count)
            for (method, mat), count in mat_method_pairs.most_common(20)
            if count >= min_frequency
        ]

        # Top entities by frequency
        for node, data in self.graph.nodes(data=True):
            freq = data.get("frequency", 0)
            if freq >= min_frequency:
                node_type = data.get("type")
                if node_type == "material":
                    patterns["top_materials"].append((node, freq))
                elif node_type == "property":
                    patterns["top_properties"].append((node, freq))
                elif node_type == "method":
                    patterns["top_methods"].append((node, freq))

        # Sort by frequency
        patterns["top_materials"] = sorted(
            patterns["top_materials"], key=lambda x: x[1], reverse=True)[:15]
        patterns["top_properties"] = sorted(
            patterns["top_properties"], key=lambda x: x[1], reverse=True)[:15]
        patterns["top_methods"] = sorted(
            patterns["top_methods"], key=lambda x: x[1], reverse=True)[:15]

        return patterns

    def identify_research_gaps(
        self,
        analyses: List[PaperAnalysis],
        min_gap_confidence: float = 0.6
    ) -> List[ResearchGap]:
        """
        Identify research gaps using graph analysis and AI.

        Args:
            analyses: List of paper analyses
            min_gap_confidence: Minimum confidence for a gap to be included

        Returns:
            List of ResearchGap objects
        """
        logger.info("Identifying research gaps...")

        gaps = []

        # Strategy 1: Find understudied material-property combinations
        studied_pairs = set()
        for u, v, d in self.graph.edges(data=True):
            if (self.graph.nodes[u].get("type") == "material" and
                    self.graph.nodes[v].get("type") == "property"):
                studied_pairs.add((u, v))

        # Get all materials and properties
        materials = [n for n, d in self.graph.nodes(
            data=True) if d.get("type") == "material"]
        properties = [n for n, d in self.graph.nodes(
            data=True) if d.get("type") == "property"]

        # Find high-frequency entities that aren't well-studied together
        top_materials = sorted(
            materials, key=lambda m: self.graph.nodes[m]["frequency"], reverse=True)[:10]
        top_properties = sorted(
            properties, key=lambda p: self.graph.nodes[p]["frequency"], reverse=True)[:10]

        understudied = []
        for mat in top_materials:
            for prop in top_properties:
                if (mat, prop) not in studied_pairs:
                    understudied.append((mat, prop))

        # Use AI to validate and describe gaps
        if understudied:
            gap_descriptions = self._generate_gap_descriptions(
                understudied[:10], analyses)

            for i, (mat, prop) in enumerate(understudied[:10]):
                if i < len(gap_descriptions):
                    gap_info = gap_descriptions[i]

                    gap = ResearchGap(
                        gap_id=f"gap_{i+1}",
                        description=gap_info["description"],
                        related_materials=[mat],
                        related_properties=[prop],
                        supporting_evidence=gap_info["evidence"],
                        confidence=gap_info["confidence"],
                        priority=gap_info["priority"]
                    )

                    if gap.confidence >= min_gap_confidence:
                        gaps.append(gap)

        # Strategy 2: Identify methodological gaps
        method_gaps = self._identify_method_gaps(analyses)
        gaps.extend(method_gaps)

        logger.info(f"Identified {len(gaps)} research gaps")
        return gaps

    def _generate_gap_descriptions(
        self,
        understudied_pairs: List[Tuple[str, str]],
        analyses: List[PaperAnalysis]
    ) -> List[Dict[str, Any]]:
        """Use AI to generate gap descriptions."""
        pairs_text = "\n".join(
            f"{i+1}. {mat} - {prop}"
            for i, (mat, prop) in enumerate(understudied_pairs)
        )

        prompt = f"""Analyze these understudied material-property combinations from scientific literature:

{pairs_text}

For each combination, determine:
1. Is this actually a research gap worth exploring? (Some combinations may not make sense)
2. Why might this be understudied?
3. What would be the research value of studying it?
4. Priority level (high/medium/low)

Return JSON array with format:
[
  {{
    "description": "Brief description of why this gap exists and why it matters",
    "evidence": ["reason1", "reason2"],
    "confidence": <float 0-1>,
    "priority": "high/medium/low"
  }}
]

Only include combinations that are scientifically meaningful. Return ONLY valid JSON.
"""

        try:
            response = self.gemini.generate_text(
                prompt=prompt,
                temperature=0.4,
                max_tokens=2000
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

            gap_descriptions = json.loads(response)
            return gap_descriptions

        except Exception as e:
            logger.error(f"Failed to generate gap descriptions: {e}")
            # Return default descriptions
            return [
                {
                    "description": f"Understudied combination of {mat} and {prop}",
                    "evidence": ["Limited research coverage"],
                    "confidence": 0.5,
                    "priority": "medium"
                }
                for mat, prop in understudied_pairs
            ]

    def _identify_method_gaps(
        self,
        analyses: List[PaperAnalysis]
    ) -> List[ResearchGap]:
        """Identify methodological gaps."""
        gaps = []

        # Count research types
        type_counter = Counter(a.research_type for a in analyses)
        total = len(analyses)

        # If computational work is underrepresented, suggest it as a gap
        computational_ratio = type_counter.get(
            "computational", 0) / total if total > 0 else 0
        if computational_ratio < 0.3:  # Less than 30% computational
            gap = ResearchGap(
                gap_id="gap_method_computational",
                description="Computational and theoretical studies are underrepresented. More simulation-based research could accelerate materials discovery.",
                related_materials=[],
                related_properties=[],
                supporting_evidence=[
                    a.arxiv_id for a in analyses if a.research_type != "computational"][:5],
                confidence=0.8,
                priority="high"
            )
            gaps.append(gap)

        return gaps

    def generate_hypotheses(
        self,
        gaps: List[ResearchGap],
        analyses: List[PaperAnalysis],
        max_hypotheses: int = 10
    ) -> List[Hypothesis]:
        """
        Generate research hypotheses based on identified gaps.

        Args:
            gaps: List of research gaps
            analyses: List of paper analyses for context
            max_hypotheses: Maximum number of hypotheses to generate

        Returns:
            List of Hypothesis objects
        """
        logger.info(f"Generating hypotheses from {len(gaps)} gaps...")

        # Select top gaps by confidence and priority
        top_gaps = sorted(
            gaps,
            key=lambda g: (
                {"high": 3, "medium": 2, "low": 1}.get(g.priority, 0),
                g.confidence
            ),
            reverse=True
        )[:5]

        hypotheses = []

        for gap in top_gaps:
            try:
                gap_hypotheses = self._generate_hypotheses_for_gap(
                    gap, analyses)
                hypotheses.extend(gap_hypotheses)

                if len(hypotheses) >= max_hypotheses:
                    break

            except Exception as e:
                logger.error(
                    f"Failed to generate hypotheses for gap {gap.gap_id}: {e}")
                continue

        hypotheses = hypotheses[:max_hypotheses]
        logger.info(f"Generated {len(hypotheses)} hypotheses")

        return hypotheses

    def _generate_hypotheses_for_gap(
        self,
        gap: ResearchGap,
        analyses: List[PaperAnalysis]
    ) -> List[Hypothesis]:
        """Generate hypotheses for a specific gap using AI."""
        # Get relevant context from analyses
        context_papers = [
            a for a in analyses
            if any(m in gap.related_materials for m in a.materials) or
            any(p in gap.related_properties for p in a.properties)
        ][:5]

        context_text = "\n\n".join([
            f"Paper: {a.title}\nKey findings: {'; '.join(a.key_findings[:2])}"
            for a in context_papers
        ])

        prompt = f"""Based on this research gap, generate 2-3 specific, testable research hypotheses:

Research Gap: {gap.description}
Related Materials: {', '.join(gap.related_materials) if gap.related_materials else 'Various'}
Related Properties: {', '.join(gap.related_properties) if gap.related_properties else 'Various'}

Context from recent research:
{context_text[:1500]}

For each hypothesis, provide:
1. A clear, specific statement of what you hypothesize
2. Rationale explaining why this hypothesis makes sense given current knowledge
3. Materials that should be investigated
4. Properties to measure/study
5. Suggested experimental or computational methods
6. Feasibility assessment (high/medium/low)
7. Novelty score (0-10, where 10 is completely novel)

Return JSON array with format:
[
  {{
    "statement": "Specific hypothesis statement",
    "rationale": "Why this hypothesis is promising",
    "materials": ["material1", "material2"],
    "properties": ["property1", "property2"],
    "methods": ["method1", "method2"],
    "feasibility": "high/medium/low",
    "novelty_score": <float 0-10>
  }}
]

Return ONLY valid JSON.
"""

        try:
            response = self.gemini.generate_text(
                prompt=prompt,
                temperature=0.7,  # Higher temp for creativity
                max_tokens=2000
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

            hyp_data = json.loads(response)

            hypotheses = []
            for i, h in enumerate(hyp_data):
                hypothesis = Hypothesis(
                    hypothesis_id=f"{gap.gap_id}_hyp_{i+1}",
                    statement=h["statement"],
                    rationale=h["rationale"],
                    related_gap=gap.gap_id,
                    materials_involved=h.get("materials", []),
                    properties_involved=h.get("properties", []),
                    suggested_methods=h.get("methods", []),
                    feasibility=h.get("feasibility", "medium"),
                    novelty_score=float(h.get("novelty_score", 5.0))
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            logger.error(f"Failed to generate hypotheses: {e}")
            return []

    def save_knowledge_graph(self, filename: str) -> Path:
        """Save knowledge graph to file."""
        filepath = self.cache_dir / f"{filename}.graphml"

        # Convert sets to lists for serialization
        graph_copy = self.graph.copy()
        for node in graph_copy.nodes():
            if "papers" in graph_copy.nodes[node]:
                graph_copy.nodes[node]["papers"] = list(
                    graph_copy.nodes[node]["papers"])

        nx.write_graphml(graph_copy, filepath)
        logger.info(f"Saved knowledge graph to: {filepath}")
        return filepath

    def load_knowledge_graph(self, filename: str) -> nx.MultiDiGraph:
        """Load knowledge graph from file."""
        if not filename.endswith('.graphml'):
            filename += '.graphml'

        filepath = self.cache_dir / filename

        self.graph = nx.read_graphml(filepath)

        # Convert lists back to sets
        for node in self.graph.nodes():
            if "papers" in self.graph.nodes[node]:
                self.graph.nodes[node]["papers"] = set(
                    self.graph.nodes[node]["papers"])

        logger.info(f"Loaded knowledge graph from: {filepath}")
        return self.graph


if __name__ == "__main__":
    from ..utils.logger import setup_logger
    from ..data_collection.paper_collector import ArXivCollector
    from .paper_analyzer import PaperAnalyzer

    setup_logger()

    logger.info("Testing KnowledgeExtractor...")

    # Get and analyze some papers
    collector = ArXivCollector()
    papers = collector.search(
        query="graphene thermal conductivity",
        max_results=10,
        categories=["cond-mat.mtrl-sci"]
    )

    analyzer = PaperAnalyzer()
    analyses = analyzer.analyze_batch(papers, max_papers=5)

    # Test knowledge extraction
    extractor = KnowledgeExtractor()

    logger.info("\n=== Test 1: Build Knowledge Graph ===")
    graph = extractor.build_knowledge_graph(analyses)
    stats = extractor.get_graph_statistics()
    logger.info(f"Graph stats: {json.dumps(stats, indent=2)}")

    logger.info("\n=== Test 2: Find Patterns ===")
    patterns = extractor.find_frequent_patterns(min_frequency=2)
    logger.info(f"Top materials: {patterns['top_materials'][:5]}")
    logger.info(f"Top properties: {patterns['top_properties'][:5]}")

    logger.info("\n=== Test 3: Identify Gaps ===")
    gaps = extractor.identify_research_gaps(analyses, min_gap_confidence=0.5)
    logger.info(f"Found {len(gaps)} research gaps")
    for gap in gaps[:3]:
        logger.info(f"\nGap: {gap.description[:150]}...")
        logger.info(
            f"Priority: {gap.priority}, Confidence: {gap.confidence:.2f}")

    logger.info("\n=== Test 4: Generate Hypotheses ===")
    hypotheses = extractor.generate_hypotheses(
        gaps, analyses, max_hypotheses=3)
    for hyp in hypotheses:
        logger.info(f"\nHypothesis: {hyp.statement}")
        logger.info(
            f"Feasibility: {hyp.feasibility}, Novelty: {hyp.novelty_score}/10")

    logger.info("\n✨ KnowledgeExtractor test completed!")
