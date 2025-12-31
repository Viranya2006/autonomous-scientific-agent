"""
Reasoning Module - Phase 3: Hypothesis Generation & Validation

This module transforms research gaps into testable scientific hypotheses
and validates their novelty and feasibility.

Components:
- HypothesisGenerator: Creates testable hypotheses from research gaps
- NoveltyChecker: Validates novelty against existing literature
- FeasibilityAnalyzer: Assesses computational and experimental feasibility
"""

from .hypothesis_generator import HypothesisGenerator
from .novelty_checker import NoveltyChecker
from .feasibility_analyzer import FeasibilityAnalyzer

__all__ = [
    'HypothesisGenerator',
    'NoveltyChecker',
    'FeasibilityAnalyzer'
]
