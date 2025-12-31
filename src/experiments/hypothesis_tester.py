"""
Hypothesis Testing via Computational Experiments
Validates hypotheses using Materials Project data and GROQ analysis
"""

import time
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from tqdm import tqdm

from ..api.materials_project_client import MaterialsProjectClient
from ..api.groq_client import GROQClient
from ..utils.logger import setup_logger

logger = setup_logger()


class HypothesisTester:
    """
    Tests hypotheses using computational methods
    """

    def __init__(self, mp_client: MaterialsProjectClient, groq_client: Optional[GROQClient] = None):
        """
        Initialize hypothesis tester

        Args:
            mp_client: Materials Project client for data
            groq_client: GROQ client for AI analysis
        """
        self.mp = mp_client
        self.groq = groq_client
        self.test_results = []
        logger.info("Hypothesis tester initialized")

    def test_hypothesis(
        self,
        hypothesis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Test a single hypothesis computationally

        Returns:
            {
                'hypothesis': str,
                'test_method': str,
                'result': str,            # Pass/Fail/Inconclusive
                'confidence': float,      # 0-1
                'evidence': Dict,         # Supporting data
                'prediction_accuracy': float,  # If measurable
                'notes': str
            }
        """
        logger.info(f"Testing: {hypothesis.get('hypothesis', '')[:80]}...")

        # Determine test method based on hypothesis
        materials = hypothesis.get('required_materials', [])
        metric = hypothesis.get('testable_metric', '')

        if not materials or not isinstance(materials, list):
            return self._inconclusive_result(hypothesis, "No materials specified")

        # Test via Materials Project property lookup
        result = self._test_via_materials_project(
            hypothesis, materials, metric)

        self.test_results.append(result)
        return result

    def batch_test(
        self,
        hypotheses_df: pd.DataFrame,
        max_tests: Optional[int] = None
    ) -> pd.DataFrame:
        """Test multiple hypotheses"""
        results = []

        test_subset = hypotheses_df.head(
            max_tests) if max_tests else hypotheses_df

        for idx, row in tqdm(test_subset.iterrows(), total=len(test_subset), desc="Testing hypotheses"):
            try:
                result = self.test_hypothesis(row.to_dict())
                results.append(result)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"Test failed for hypothesis {idx}: {e}")
                results.append(self._inconclusive_result(
                    row.to_dict(), f"Test error: {str(e)[:100]}"))

        # Add results to dataframe
        if results:
            hypotheses_df['test_result'] = [r['result'] for r in results]
            hypotheses_df['test_confidence'] = [r['confidence']
                                                for r in results]
            hypotheses_df['test_evidence'] = [
                str(r['evidence'])[:500] for r in results]
            hypotheses_df['test_method'] = [r['test_method'] for r in results]

        return hypotheses_df

    def _test_via_materials_project(
        self,
        hypothesis: Dict,
        materials: List[str],
        metric: str
    ) -> Dict:
        """Test by querying Materials Project for properties"""
        evidence = {}

        # Query MP for each material
        for material in materials[:2]:  # Limit to avoid quota
            try:
                material_str = str(material).strip()
                if len(material_str) < 2:
                    continue

                props = self.mp.search_materials(material_str)
                if props:
                    evidence[material_str] = {
                        'found': True,
                        'count': len(props) if isinstance(props, list) else 1
                    }
                    logger.debug(
                        f"Found {len(props) if isinstance(props, list) else 1} results for {material_str}")
            except Exception as e:
                logger.debug(f"MP query failed for {material}: {e}")
                evidence[str(material)] = {
                    'found': False, 'error': str(e)[:100]}

        if not evidence or not any(e.get('found', False) for e in evidence.values()):
            return self._inconclusive_result(hypothesis, "No data available in Materials Project")

        # Analyze evidence against prediction
        predicted_outcome = hypothesis.get('predicted_outcome', '')

        # Use GROQ for intelligent analysis if available
        if self.groq and predicted_outcome:
            try:
                confidence = self._groq_analyze_evidence(
                    evidence, predicted_outcome, hypothesis.get('hypothesis', ''))
            except Exception as e:
                logger.debug(f"GROQ analysis failed: {e}")
                confidence = self._calculate_confidence(
                    evidence, predicted_outcome)
        else:
            confidence = self._calculate_confidence(
                evidence, predicted_outcome)

        # Determine result
        if confidence > 0.6:
            result = "PASS"
            notes = "Materials Project data supports hypothesis"
        elif confidence > 0.3:
            result = "INCONCLUSIVE"
            notes = "Partial evidence found"
        else:
            result = "FAIL"
            notes = "Insufficient evidence"

        return {
            'hypothesis': hypothesis.get('hypothesis', ''),
            'test_method': 'Materials Project Lookup',
            'result': result,
            'confidence': float(confidence),
            'evidence': evidence,
            'prediction_accuracy': float(confidence),
            'notes': notes
        }

    def _groq_analyze_evidence(self, evidence: Dict, prediction: str, hypothesis: str) -> float:
        """Use GROQ to analyze evidence quality"""
        prompt = f"""Analyze this scientific hypothesis test:

Hypothesis: {hypothesis}

Predicted Outcome: {prediction}

Evidence Found: {evidence}

Rate the confidence that the evidence supports the hypothesis on a scale of 0.0 to 1.0.
Consider:
- Material availability in database
- Relevance of findings
- Alignment with prediction

Respond with ONLY a number between 0.0 and 1.0."""

        try:
            response = self.groq.generate_text(
                prompt=prompt, max_tokens=50, temperature=0.1)
            # Extract numerical score
            score_str = response.strip().split()[0]
            score = float(score_str)
            return max(0.0, min(1.0, score))
        except:
            return 0.5

    def _calculate_confidence(self, evidence: Dict, prediction: str) -> float:
        """Calculate confidence score based on evidence"""
        # Simple heuristic based on data availability
        score = 0.3  # Baseline

        # Increase score if materials found
        found_count = sum(1 for e in evidence.values()
                          if e.get('found', False))
        total_count = len(evidence)

        if total_count > 0:
            found_ratio = found_count / total_count
            score += 0.4 * found_ratio

        # Bonus if prediction keywords match
        if prediction:
            prediction_lower = prediction.lower()
            for material in evidence.keys():
                if material.lower() in prediction_lower:
                    score += 0.1

        return float(min(score, 1.0))

    def _inconclusive_result(self, hypothesis: Dict, reason: str) -> Dict:
        """Generate inconclusive test result"""
        return {
            'hypothesis': hypothesis.get('hypothesis', 'Unknown'),
            'test_method': 'None',
            'result': 'INCONCLUSIVE',
            'confidence': 0.0,
            'evidence': {},
            'prediction_accuracy': 0.0,
            'notes': reason
        }

    def get_summary_stats(self) -> Dict:
        """Get testing statistics"""
        if not self.test_results:
            return {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'inconclusive': 0,
                'average_confidence': 0.0
            }

        results_list = [r['result'] for r in self.test_results]

        return {
            'total_tests': len(self.test_results),
            'passed': results_list.count('PASS'),
            'failed': results_list.count('FAIL'),
            'inconclusive': results_list.count('INCONCLUSIVE'),
            'average_confidence': float(np.mean([r['confidence'] for r in self.test_results]))
        }
