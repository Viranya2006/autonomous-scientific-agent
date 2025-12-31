"""
Tests for Phase 2: Paper Collection and Analysis

Run with: pytest tests/test_phase2.py -v
"""

from src.api.groq_client import GROQClient
from src.analysis.knowledge_extractor import KnowledgeExtractor, ResearchGap, Hypothesis
from src.analysis.paper_analyzer import PaperAnalyzer, PaperAnalysis
from src.data_collection.paper_collector import ArXivCollector, Paper, search_materials_papers
import sys
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestArXivCollector:
    """Test ArXiv paper collection."""

    def test_collector_initialization(self):
        """Test collector initializes correctly."""
        collector = ArXivCollector()
        assert collector.cache_dir.exists()
        assert collector.BASE_URL == "http://export.arxiv.org/api/query"

    def test_basic_search(self):
        """Test basic paper search."""
        collector = ArXivCollector()
        papers = collector.search(
            query="quantum computing",
            max_results=5
        )

        assert len(papers) > 0
        assert len(papers) <= 5

        # Check paper structure
        paper = papers[0]
        assert hasattr(paper, 'arxiv_id')
        assert hasattr(paper, 'title')
        assert hasattr(paper, 'abstract')
        assert hasattr(paper, 'authors')
        assert len(paper.title) > 0
        assert len(paper.abstract) > 0

    def test_category_filter(self):
        """Test searching with category filters."""
        collector = ArXivCollector()
        papers = collector.search(
            query="materials",
            max_results=3,
            categories=["cond-mat.mtrl-sci"]
        )

        assert len(papers) > 0
        for paper in papers:
            # Primary category should be materials science
            assert "cond-mat.mtrl-sci" in paper.categories

    def test_recent_papers(self):
        """Test searching for recent papers."""
        collector = ArXivCollector()
        papers = collector.search_recent(
            query="machine learning",
            days=7,
            max_results=3
        )

        assert len(papers) > 0

    def test_save_and_load(self):
        """Test saving and loading papers."""
        collector = ArXivCollector()
        papers = collector.search(
            query="test query",
            max_results=2
        )

        # Save papers
        filepath = collector.save_papers(
            papers, "test_papers_temp", format="json")
        assert filepath.exists()

        # Load papers
        loaded = collector.load_papers("test_papers_temp")
        assert len(loaded) == len(papers)
        assert loaded[0].arxiv_id == papers[0].arxiv_id

        # Cleanup
        filepath.unlink()

    def test_dataframe_conversion(self):
        """Test converting papers to DataFrame."""
        collector = ArXivCollector()
        papers = collector.search(query="test", max_results=3)

        df = collector.get_papers_dataframe(papers)
        assert len(df) == len(papers)
        assert 'title' in df.columns
        assert 'abstract' in df.columns
        assert 'arxiv_id' in df.columns


class TestGROQClient:
    """Test GROQ API client."""

    def test_client_initialization(self):
        """Test GROQ client initializes."""
        client = GROQClient()
        assert client.model == "llama-3.1-8b-instant"
        assert client.base_url == "https://api.groq.com/openai/v1/chat/completions"

    def test_text_generation(self):
        """Test basic text generation."""
        client = GROQClient()
        response = client.generate_text(
            prompt="Say 'test successful' if you can read this.",
            max_tokens=20,
            temperature=0.0
        )

        assert isinstance(response, str)
        assert len(response) > 0

    def test_entity_extraction(self):
        """Test entity extraction."""
        client = GROQClient()
        text = "Graphene exhibits high thermal conductivity and excellent electrical properties."

        entities = client.extract_entities(text)

        assert isinstance(entities, dict)
        # Should extract materials and properties
        if entities.get("materials"):
            assert any("graphene" in m.lower() for m in entities["materials"])

    def test_classification(self):
        """Test text classification."""
        client = GROQClient()
        text = "We performed DFT calculations to study electronic structure."

        result = client.classify_text(
            text=text,
            categories=["experimental", "theoretical", "computational"],
            multi_label=False
        )

        assert "categories" in result
        assert len(result["categories"]) > 0


class TestPaperAnalyzer:
    """Test paper analysis system."""

    @pytest.fixture
    def sample_papers(self):
        """Get sample papers for testing."""
        collector = ArXivCollector()
        papers = collector.search(
            query="graphene",
            max_results=2,
            categories=["cond-mat.mtrl-sci"]
        )
        return papers

    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        analyzer = PaperAnalyzer()
        assert analyzer.gemini is not None
        assert analyzer.groq is not None
        assert analyzer.cache_dir.exists()

    def test_single_paper_analysis(self, sample_papers):
        """Test analyzing a single paper."""
        analyzer = PaperAnalyzer()
        paper = sample_papers[0]

        analysis = analyzer.analyze_paper(paper, skip_cache=True)

        # Check analysis structure
        assert isinstance(analysis, PaperAnalysis)
        assert analysis.arxiv_id == paper.arxiv_id
        assert analysis.title == paper.title
        assert 0 <= analysis.relevance_score <= 10
        assert 0 <= analysis.confidence_score <= 1

        # Check extracted entities
        assert isinstance(analysis.materials, list)
        assert isinstance(analysis.properties, list)
        assert isinstance(analysis.methods, list)

        # Check deep analysis fields
        assert isinstance(analysis.key_findings, list)
        assert len(analysis.research_significance) > 0
        assert analysis.research_type in [
            "experimental", "theoretical", "computational", "review", "unknown"]

    def test_batch_analysis(self, sample_papers):
        """Test batch paper analysis."""
        analyzer = PaperAnalyzer()

        analyses = analyzer.analyze_batch(
            sample_papers,
            max_papers=2
        )

        assert len(analyses) <= 2
        assert all(isinstance(a, PaperAnalysis) for a in analyses)

    def test_dataframe_conversion(self, sample_papers):
        """Test converting analyses to DataFrame."""
        analyzer = PaperAnalyzer()
        analyses = analyzer.analyze_batch(sample_papers, max_papers=1)

        df = analyzer.get_analysis_dataframe(analyses)
        assert len(df) == len(analyses)
        assert 'relevance_score' in df.columns
        assert 'research_type' in df.columns


class TestKnowledgeExtractor:
    """Test knowledge extraction and hypothesis generation."""

    @pytest.fixture
    def sample_analyses(self):
        """Get sample analyses for testing."""
        collector = ArXivCollector()
        papers = collector.search(
            query="graphene thermal conductivity",
            max_results=5,
            categories=["cond-mat.mtrl-sci"]
        )

        analyzer = PaperAnalyzer()
        analyses = analyzer.analyze_batch(papers, max_papers=3)
        return analyses

    def test_extractor_initialization(self):
        """Test extractor initializes correctly."""
        extractor = KnowledgeExtractor()
        assert extractor.gemini is not None
        assert extractor.cache_dir.exists()
        assert extractor.graph is not None

    def test_knowledge_graph_building(self, sample_analyses):
        """Test building knowledge graph from analyses."""
        extractor = KnowledgeExtractor()
        graph = extractor.build_knowledge_graph(sample_analyses)

        assert graph.number_of_nodes() > 0
        assert graph.number_of_edges() > 0

        # Check node types exist
        node_types = set(data.get("type")
                         for _, data in graph.nodes(data=True))
        assert "material" in node_types or "property" in node_types or "method" in node_types

    def test_graph_statistics(self, sample_analyses):
        """Test getting graph statistics."""
        extractor = KnowledgeExtractor()
        extractor.build_knowledge_graph(sample_analyses)

        stats = extractor.get_graph_statistics()

        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "num_materials" in stats
        assert "num_properties" in stats
        assert stats["total_nodes"] > 0

    def test_pattern_finding(self, sample_analyses):
        """Test finding frequent patterns."""
        extractor = KnowledgeExtractor()
        extractor.build_knowledge_graph(sample_analyses)

        patterns = extractor.find_frequent_patterns(min_frequency=1)

        assert "top_materials" in patterns
        assert "top_properties" in patterns
        assert "material_property_pairs" in patterns
        assert isinstance(patterns["top_materials"], list)

    def test_gap_identification(self, sample_analyses):
        """Test identifying research gaps."""
        extractor = KnowledgeExtractor()
        extractor.build_knowledge_graph(sample_analyses)

        gaps = extractor.identify_research_gaps(
            sample_analyses,
            min_gap_confidence=0.5
        )

        assert isinstance(gaps, list)
        if len(gaps) > 0:
            gap = gaps[0]
            assert isinstance(gap, ResearchGap)
            assert hasattr(gap, 'description')
            assert hasattr(gap, 'confidence')
            assert 0 <= gap.confidence <= 1

    def test_hypothesis_generation(self, sample_analyses):
        """Test generating research hypotheses."""
        extractor = KnowledgeExtractor()
        extractor.build_knowledge_graph(sample_analyses)

        gaps = extractor.identify_research_gaps(
            sample_analyses,
            min_gap_confidence=0.5
        )

        if len(gaps) > 0:
            hypotheses = extractor.generate_hypotheses(
                gaps,
                sample_analyses,
                max_hypotheses=3
            )

            assert isinstance(hypotheses, list)
            if len(hypotheses) > 0:
                hyp = hypotheses[0]
                assert isinstance(hyp, Hypothesis)
                assert len(hyp.statement) > 0
                assert len(hyp.rationale) > 0
                assert 0 <= hyp.novelty_score <= 10


class TestIntegration:
    """Integration tests for complete pipeline."""

    def test_end_to_end_pipeline(self):
        """Test complete pipeline from collection to hypothesis generation."""
        # Step 1: Collect papers
        collector = ArXivCollector()
        papers = collector.search(
            query="2D materials electronic properties",
            max_results=3,
            categories=["cond-mat.mtrl-sci"]
        )
        assert len(papers) > 0

        # Step 2: Analyze papers
        analyzer = PaperAnalyzer()
        analyses = analyzer.analyze_batch(papers, max_papers=2)
        assert len(analyses) > 0

        # Step 3: Extract knowledge
        extractor = KnowledgeExtractor()
        graph = extractor.build_knowledge_graph(analyses)
        assert graph.number_of_nodes() > 0

        # Step 4: Identify gaps
        gaps = extractor.identify_research_gaps(
            analyses, min_gap_confidence=0.5)
        # Gaps might be empty, that's okay for small datasets

        # Step 5: Generate hypotheses
        if len(gaps) > 0:
            hypotheses = extractor.generate_hypotheses(
                gaps, analyses, max_hypotheses=2)
            # Hypotheses depend on gaps, might be empty

        # If we got this far without errors, pipeline works
        assert True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
