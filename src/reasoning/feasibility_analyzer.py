"""
Feasibility Analyzer - Assesses computational and experimental feasibility

Evaluates whether hypotheses can be validated using available tools,
data sources, and computational methods.
"""

import time
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from tqdm import tqdm

from ..api.materials_project_client import MaterialsProjectClient
from ..utils.logger import setup_logger

logger = setup_logger()


class FeasibilityAnalyzer:
    """
    Analyzes computational and experimental feasibility of hypotheses
    """

    def __init__(
        self,
        mp_client: MaterialsProjectClient,
        available_methods: List[str] = None
    ):
        """
        Initialize feasibility analyzer

        Args:
            mp_client: Materials Project client for data queries
            available_methods: List of available simulation methods
        """
        self.mp = mp_client
        self.available_methods = available_methods or [
            'DFT', 'molecular_dynamics', 'monte_carlo',
            'property_prediction', 'structure_optimization',
            'machine_learning', 'computational_screening'
        ]
        logger.info("Feasibility analyzer initialized")

    def analyze_feasibility(
        self,
        hypothesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive feasibility analysis

        Returns:
            {
                'feasibility_score': float,     # 0-1 (1 = highly feasible)
                'feasibility_level': str,       # Easy/Medium/Hard/Infeasible
                'data_available': bool,         # Can we get required data?
                'methods_available': bool,      # Can we simulate this?
                'time_estimate': str,           # Estimated computation time
                'resource_requirements': Dict,  # What's needed
                'key_challenges': List[str],    # Main obstacles
                'recommendations': List[str]    # How to proceed
            }
        """
        try:
            # Check material data availability
            data_check = self._check_data_availability(hypothesis)

            # Check simulation methods
            methods_check = self._check_methods(hypothesis)

            # Estimate complexity
            complexity = self._estimate_complexity(hypothesis)

            # Calculate overall feasibility
            feasibility_score = (
                0.4 * data_check['score'] +
                0.3 * methods_check['score'] +
                0.3 * (1 - complexity['score'])
            )

            # Determine level
            if feasibility_score > 0.7:
                level = 'Easy'
            elif feasibility_score > 0.5:
                level = 'Medium'
            elif feasibility_score > 0.3:
                level = 'Hard'
            else:
                level = 'Infeasible'

            return {
                'feasibility_score': float(feasibility_score),
                'feasibility_level': level,
                'data_available': data_check['available'],
                'methods_available': methods_check['available'],
                'time_estimate': complexity['time_estimate'],
                'resource_requirements': {
                    'materials': hypothesis.get('required_materials', []),
                    'methods': hypothesis.get('required_methods', []),
                    'data_sources': data_check['sources']
                },
                'key_challenges': self._identify_challenges(hypothesis, data_check, methods_check, complexity),
                'recommendations': self._generate_recommendations(hypothesis, feasibility_score)
            }

        except Exception as e:
            logger.error(f"Feasibility analysis failed: {e}")
            return self._default_feasibility()

    def batch_analyze(
        self,
        hypotheses_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Analyze feasibility for all hypotheses"""
        results = []

        for idx, row in tqdm(hypotheses_df.iterrows(), total=len(hypotheses_df), desc="Analyzing feasibility"):
            result = self.analyze_feasibility(row.to_dict())
            results.append(result)
            time.sleep(0.5)  # Rate limiting for MP API

        # Add results to dataframe
        hypotheses_df['feasibility_score'] = [
            r['feasibility_score'] for r in results]
        hypotheses_df['feasibility_level'] = [
            r['feasibility_level'] for r in results]
        hypotheses_df['data_available'] = [r['data_available']
                                           for r in results]
        hypotheses_df['time_estimate'] = [r['time_estimate'] for r in results]
        hypotheses_df['key_challenges'] = [
            ', '.join(r['key_challenges']) for r in results]

        return hypotheses_df

    def _check_data_availability(self, hypothesis: Dict) -> Dict:
        """Check if required material data exists in Materials Project"""
        materials = hypothesis.get('required_materials', [])

        if not materials or not isinstance(materials, list):
            return {'available': False, 'score': 0.3, 'sources': []}

        found_count = 0
        sources = []

        # Check first 3 materials to avoid quota issues
        for material in materials[:3]:
            try:
                if not material or len(str(material).strip()) < 2:
                    continue

                # Simple check - query Materials Project
                results = self.mp.search_materials(str(material).strip())
                if results:
                    found_count += 1
                    sources.append(f"Materials Project: {material}")

            except Exception as e:
                logger.debug(f"MP query failed for {material}: {e}")

        availability_score = found_count / len(materials) if materials else 0

        return {
            'available': availability_score > 0.3,
            'score': float(availability_score),
            'sources': sources
        }

    def _check_methods(self, hypothesis: Dict) -> Dict:
        """Check if required methods are available"""
        required = hypothesis.get('required_methods', [])

        if not required or not isinstance(required, list):
            # Assume feasible if unspecified
            return {'available': True, 'score': 0.8}

        # Check overlap with available methods
        available_count = sum(
            1 for method in required
            if any(avail.lower() in str(method).lower() for avail in self.available_methods)
        )

        score = available_count / len(required) if required else 0.8

        return {
            'available': score > 0.5,
            'score': float(score)
        }

    def _estimate_complexity(self, hypothesis: Dict) -> Dict:
        """Estimate computational complexity"""
        # Simple heuristic based on hypothesis length and keywords
        text = str(hypothesis.get('hypothesis', ''))

        complexity_keywords = {
            'high': ['quantum', 'molecular dynamics', 'ab initio', 'DFT',
                     'optimization', 'simulation', 'machine learning'],
            'medium': ['calculation', 'prediction', 'modeling', 'analysis',
                       'screening', 'property'],
            'low': ['estimate', 'comparison', 'survey', 'review']
        }

        complexity_score = 0.5  # Default medium

        text_lower = text.lower()
        for keyword in complexity_keywords['high']:
            if keyword.lower() in text_lower:
                complexity_score = 0.8
                break

        if complexity_score < 0.7:  # Check low only if not high
            for keyword in complexity_keywords['low']:
                if keyword.lower() in text_lower:
                    complexity_score = 0.3
                    break

        # Estimate time based on complexity
        if complexity_score > 0.7:
            time_estimate = "12-24 hours"
        elif complexity_score > 0.4:
            time_estimate = "2-6 hours"
        else:
            time_estimate = "< 1 hour"

        return {
            'score': float(complexity_score),
            'time_estimate': time_estimate
        }

    def _identify_challenges(self, hypothesis, data_check, methods_check, complexity) -> List[str]:
        """Identify key challenges"""
        challenges = []

        if not data_check['available']:
            challenges.append("Limited material property data available")

        if not methods_check['available']:
            challenges.append(
                "Required simulation methods not readily available")

        if complexity['score'] > 0.7:
            challenges.append("High computational complexity")

        if not hypothesis.get('testable_metric'):
            challenges.append("Success metric not clearly defined")

        return challenges or ["No major challenges identified"]

    def _generate_recommendations(self, hypothesis, feasibility_score) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if feasibility_score > 0.7:
            recommendations.append("Proceed with computational validation")
            recommendations.append("Prepare simulation environment")
        elif feasibility_score > 0.5:
            recommendations.append("Gather additional material data first")
            recommendations.append("Consider simplified initial experiments")
        else:
            recommendations.append(
                "Refine hypothesis to be more computationally tractable")
            recommendations.append("Seek alternative validation approaches")

        return recommendations

    def _default_feasibility(self) -> Dict:
        """Return default feasibility result for errors"""
        return {
            'feasibility_score': 0.5,
            'feasibility_level': 'Medium',
            'data_available': False,
            'methods_available': False,
            'time_estimate': 'Unknown',
            'resource_requirements': {'materials': [], 'methods': [], 'data_sources': []},
            'key_challenges': ['Analysis failed'],
            'recommendations': ['Review hypothesis and retry']
        }
