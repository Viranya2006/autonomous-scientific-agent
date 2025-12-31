"""
Unit tests for Phase 3: Hypothesis Generation & Validation
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock

from src.reasoning.hypothesis_generator import HypothesisGenerator
from src.reasoning.novelty_checker import NoveltyChecker
from src.reasoning.feasibility_analyzer import FeasibilityAnalyzer


class TestHypothesisGenerator:
    """Tests for hypothesis generation"""

    def test_hypothesis_generation_basic(self):
        """Test basic hypothesis generation"""
        # Mock clients
        gemini = Mock()
        groq = Mock()
        groq.generate_text = Mock(
            return_value="HYPOTHESIS 1: If we dope silicon with phosphorus, then conductivity increases because of electron donation.")

        generator = HypothesisGenerator(gemini, groq)

        gap = {
            'description': 'Low-temperature sodium-ion conductivity is poorly understood',
            'domain': 'battery materials',
            'score': 8.0
        }

        hypotheses = generator.generate_from_gap(gap, num_hypotheses=2)

        assert isinstance(hypotheses, list)
        assert len(hypotheses) > 0

    def test_parse_hypothesis_list(self):
        """Test parsing GROQ response"""
        gemini = Mock()
        groq = Mock()
        generator = HypothesisGenerator(gemini, groq)

        text = """HYPOTHESIS 1: If we dope material A, then property X increases.
        
HYPOTHESIS 2: Combining B with C should yield improved performance.

HYPOTHESIS 3: Testing under conditions D will reveal mechanism E."""

        hypotheses = generator._parse_hypothesis_list(text)

        assert len(hypotheses) == 3
        assert all(len(h) > 50 for h in hypotheses)

    def test_extract_score(self):
        """Test score extraction"""
        gemini = Mock()
        groq = Mock()
        generator = HypothesisGenerator(gemini, groq)

        # Test various formats
        assert generator._extract_score("8 - High novelty") == 0.8
        assert generator._extract_score("5.5/10") == 0.55
        assert generator._extract_score("No score") == 0.5


class TestNoveltyChecker:
    """Tests for novelty checking"""

    def test_novelty_checking_basic(self):
        """Test basic novelty check"""
        papers_df = pd.DataFrame({
            'title': ['Silicon Solar Cells', 'Perovskite Batteries'],
            'abstract': ['Silicon-based photovoltaic cells...', 'Novel perovskite battery materials...']
        })

        checker = NoveltyChecker(papers_df)

        result = checker.check_novelty(
            "Novel quantum battery design using europium")

        assert 'novelty_score' in result
        assert 0 <= result['novelty_score'] <= 1
        assert 'is_novel' in result
        assert isinstance(result['is_novel'], bool)

    def test_novelty_with_similar_content(self):
        """Test novelty detection with similar content"""
        papers_df = pd.DataFrame({
            'title': ['Quantum Battery Design', 'Battery Quantum Effects'],
            'abstract': ['Quantum battery using europium...', 'Europium in quantum batteries...']
        })

        checker = NoveltyChecker(papers_df)

        result = checker.check_novelty(
            "Novel quantum battery design using europium")

        # Should have lower novelty due to similar papers
        assert result['novelty_score'] < 0.8

    def test_batch_check(self):
        """Test batch novelty checking"""
        papers_df = pd.DataFrame({
            'title': ['Paper 1', 'Paper 2'],
            'abstract': ['Content 1', 'Content 2']
        })

        checker = NoveltyChecker(papers_df)

        hypotheses_df = pd.DataFrame({
            'hypothesis': ['Hypothesis A', 'Hypothesis B']
        })

        result_df = checker.batch_check(hypotheses_df)

        assert 'novelty_score' in result_df.columns
        assert 'is_novel' in result_df.columns
        assert len(result_df) == 2


class TestFeasibilityAnalyzer:
    """Tests for feasibility analysis"""

    def test_feasibility_analysis_basic(self):
        """Test basic feasibility analysis"""
        mp_client = Mock()
        mp_client.search_materials = Mock(
            return_value=[{'material_id': 'mp-123'}])

        analyzer = FeasibilityAnalyzer(mp_client)

        hypothesis = {
            'hypothesis': 'Doping silicon with phosphorus improves conductivity',
            'required_materials': ['Silicon', 'Phosphorus'],
            'required_methods': ['DFT', 'property prediction']
        }

        result = analyzer.analyze_feasibility(hypothesis)

        assert 'feasibility_score' in result
        assert 'feasibility_level' in result
        assert result['feasibility_level'] in [
            'Easy', 'Medium', 'Hard', 'Infeasible']

    def test_complexity_estimation(self):
        """Test complexity estimation"""
        mp_client = Mock()
        analyzer = FeasibilityAnalyzer(mp_client)

        # High complexity
        hyp_high = {
            'hypothesis': 'Perform quantum molecular dynamics simulation'}
        complexity_high = analyzer._estimate_complexity(hyp_high)
        assert complexity_high['score'] > 0.6

        # Low complexity
        hyp_low = {'hypothesis': 'Estimate property using simple comparison'}
        complexity_low = analyzer._estimate_complexity(hyp_low)
        assert complexity_low['score'] < 0.5

    def test_batch_analyze(self):
        """Test batch feasibility analysis"""
        mp_client = Mock()
        mp_client.search_materials = Mock(return_value=[])

        analyzer = FeasibilityAnalyzer(mp_client)

        hypotheses_df = pd.DataFrame({
            'hypothesis': ['Hypothesis A', 'Hypothesis B'],
            'required_materials': [['Material1'], ['Material2']],
            'required_methods': [['DFT'], ['Modeling']]
        })

        result_df = analyzer.batch_analyze(hypotheses_df)

        assert 'feasibility_score' in result_df.columns
        assert 'feasibility_level' in result_df.columns
        assert len(result_df) == 2


class TestIntegration:
    """Integration tests for Phase 3 pipeline"""

    def test_full_pipeline_mock(self):
        """Test full hypothesis generation pipeline with mocks"""
        # Mock API clients
        gemini = Mock()
        groq = Mock()
        mp = Mock()

        groq.generate_text = Mock(
            return_value="HYPOTHESIS 1: Test hypothesis about materials.")
        gemini.generate_text = Mock(
            return_value="**Refined Hypothesis**: Improved test hypothesis.")
        mp.search_materials = Mock(return_value=[{'id': '1'}])

        # Create components
        generator = HypothesisGenerator(gemini, groq)

        # Generate hypothesis
        gap = {
            'description': 'Test gap',
            'domain': 'materials',
            'score': 8.0
        }

        hypotheses = generator.generate_from_gap(gap, num_hypotheses=1)

        assert len(hypotheses) > 0
        assert 'hypothesis' in hypotheses[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
