"""
Hypothesis Generator - Transforms research gaps into testable hypotheses

Generates novel, specific, and testable scientific hypotheses from identified
research gaps using dual-AI approach (GROQ for speed, Gemini for quality).
"""

import time
import re
from typing import Dict, Any, List, Optional
import pandas as pd
from tqdm import tqdm

from ..api.gemini_client import GeminiClient
from ..api.groq_client import GROQClient
from ..utils.logger import setup_logger

logger = setup_logger()


class HypothesisGenerator:
    """
    Generates testable scientific hypotheses from research gaps
    """

    def __init__(
        self,
        gemini_client: GeminiClient,
        groq_client: GROQClient,
        creativity_level: float = 0.7
    ):
        """
        Initialize hypothesis generator

        Args:
            gemini_client: For high-quality hypothesis refinement
            groq_client: For fast bulk generation
            creativity_level: Temperature for generation (0-1)
        """
        self.gemini = gemini_client
        self.groq = groq_client
        self.creativity = creativity_level
        self.hypothesis_templates = self._load_templates()
        logger.info("Hypothesis generator initialized")

    def generate_from_gap(
        self,
        gap: Dict[str, Any],
        num_hypotheses: int = 5,
        use_templates: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple hypotheses from a single research gap

        Args:
            gap: Research gap dict with 'description', 'domain', 'score'
            num_hypotheses: Number of variants to generate
            use_templates: Use structured templates for consistency

        Returns:
            List of hypothesis dicts with complete metadata
        """
        try:
            # Step 1: Use GROQ for fast bulk generation
            hypotheses = self._generate_bulk_with_groq(gap, num_hypotheses)

            if not hypotheses:
                logger.warning(
                    f"No hypotheses generated for gap: {gap.get('description', '')[:50]}")
                return []

            # Step 2: Refine top candidates with Gemini (if available)
            refined = self._refine_with_gemini(
                hypotheses[:min(3, len(hypotheses))], gap)

            # Step 3: Structure and validate
            structured = self._structure_hypotheses(refined, gap)

            return structured

        except Exception as e:
            logger.error(f"Failed to generate hypotheses: {e}")
            return []

    def generate_from_all_gaps(
        self,
        gaps: List[Dict],
        hypotheses_per_gap: int = 3,
        max_total: int = 50
    ) -> pd.DataFrame:
        """
        Generate hypotheses from all research gaps

        Args:
            gaps: List of research gap dicts
            hypotheses_per_gap: Hypotheses to generate per gap
            max_total: Maximum total hypotheses

        Returns:
            DataFrame with all generated hypotheses
        """
        all_hypotheses = []

        # Sort gaps by score (focus on high-impact)
        sorted_gaps = sorted(
            gaps, key=lambda x: x.get('score', 0), reverse=True)

        for gap in tqdm(sorted_gaps, desc="Generating hypotheses"):
            if len(all_hypotheses) >= max_total:
                break

            hyps = self.generate_from_gap(
                gap, num_hypotheses=hypotheses_per_gap)
            all_hypotheses.extend(hyps)

            time.sleep(1)  # Respect rate limits

        df = pd.DataFrame(all_hypotheses)
        logger.success(f"Generated {len(df)} total hypotheses")
        return df

    def _generate_bulk_with_groq(
        self,
        gap: Dict,
        num: int
    ) -> List[str]:
        """
        Fast hypothesis generation using GROQ
        """
        prompt = f"""You are a materials science researcher. Generate {num} specific, testable hypotheses to address this research gap:

Gap: {gap['description']}
Domain: {gap.get('domain', 'materials science')}
Current Knowledge: {gap.get('context', 'Limited experimental data available')}

Generate hypotheses in this exact format:

HYPOTHESIS 1: If we [specific action], then [predicted outcome] because [scientific reasoning].

Requirements:
- Be specific (mention exact materials, conditions, values)
- Be testable (can be validated computationally or experimentally)
- Be novel (address the unexplored aspect of the gap)
- Include quantitative predictions where possible

Generate {num} hypotheses now:"""

        try:
            response = self.groq.generate_text(
                prompt=prompt,
                max_tokens=800,
                temperature=self.creativity
            )

            # Parse individual hypotheses
            hypotheses = self._parse_hypothesis_list(response)
            logger.debug(f"Generated {len(hypotheses)} hypotheses with GROQ")
            return hypotheses

        except Exception as e:
            logger.error(f"GROQ generation failed: {e}")
            return []

    def _refine_with_gemini(
        self,
        hypotheses: List[str],
        gap: Dict
    ) -> List[Dict]:
        """
        Refine and structure hypotheses using Gemini
        """
        refined = []

        for hyp in hypotheses:
            prompt = f"""Analyze and refine this scientific hypothesis:

{hyp}

Provide a structured analysis:

**Refined Hypothesis**:
[Improved, more precise version]

**Scientific Reasoning**:
[Detailed explanation of why this should work]

**Predicted Outcome**:
[Specific, quantitative prediction]

**Testable Metric**:
[How to measure success - exact property/value]

**Materials Required**:
[List specific materials needed]

**Methods Required**:
[List experimental/computational techniques]

**Novelty Assessment** (0-10):
[Score] - [Brief justification]

**Feasibility** (Easy/Medium/Hard):
[Assessment] - [Key challenges]
"""

            try:
                response = self.gemini.generate_text(
                    prompt=prompt,
                    temperature=0.3,  # Lower for analytical task
                    max_tokens=600
                )

                structured = self._parse_gemini_analysis(response, hyp, gap)
                refined.append(structured)

                time.sleep(1.5)  # Rate limiting

            except Exception as e:
                logger.warning(
                    f"Gemini refinement failed: {e}, using original")
                refined.append({
                    'hypothesis': hyp,
                    'refined': False,
                    'source_gap': gap.get('description', '')
                })

        return refined

    def _structure_hypotheses(
        self,
        refined: List[Dict],
        gap: Dict
    ) -> List[Dict]:
        """
        Create final structured hypothesis objects
        """
        structured = []

        for item in refined:
            hyp = {
                'hypothesis': item.get('refined_hypothesis', item.get('hypothesis')),
                'reasoning': item.get('reasoning', ''),
                'predicted_outcome': item.get('predicted_outcome', ''),
                'testable_metric': item.get('testable_metric', ''),
                'required_materials': item.get('materials', []),
                'required_methods': item.get('methods', []),
                'novelty_estimate': item.get('novelty', 0.5),
                'feasibility': item.get('feasibility', 'Medium'),
                'source_gap': gap.get('description', ''),
                'source_paper': gap.get('source_paper', ''),
                'gap_score': gap.get('score', 5.0),
                'generated_at': pd.Timestamp.now().isoformat()
            }
            structured.append(hyp)

        return structured

    def _parse_hypothesis_list(self, text: str) -> List[str]:
        """Extract individual hypotheses from GROQ response"""
        lines = text.split('\n')
        hypotheses = []
        current = []

        for line in lines:
            if line.strip().startswith('HYPOTHESIS'):
                if current:
                    hypotheses.append(' '.join(current))
                current = [line.split(':', 1)[1].strip()
                           if ':' in line else line]
            elif current and line.strip():
                current.append(line.strip())

        if current:
            hypotheses.append(' '.join(current))

        # Filter short/bad parses
        return [h for h in hypotheses if len(h) > 50]

    def _parse_gemini_analysis(self, response: str, original: str, gap: Dict) -> Dict:
        """Parse structured Gemini response"""
        # Simple parsing - look for section headers
        sections = {}
        current_section = None
        current_content = []

        for line in response.split('\n'):
            if line.startswith('**') and line.endswith('**:'):
                if current_section:
                    sections[current_section] = ' '.join(
                        current_content).strip()
                current_section = line.strip('*:').lower().replace(' ', '_')
                current_content = []
            elif current_section:
                current_content.append(line.strip())

        if current_section:
            sections[current_section] = ' '.join(current_content).strip()

        return {
            'hypothesis': original,
            'refined_hypothesis': sections.get('refined_hypothesis', original),
            'reasoning': sections.get('scientific_reasoning', ''),
            'predicted_outcome': sections.get('predicted_outcome', ''),
            'testable_metric': sections.get('testable_metric', ''),
            'materials': self._extract_list(sections.get('materials_required', '')),
            'methods': self._extract_list(sections.get('methods_required', '')),
            'novelty': self._extract_score(sections.get('novelty_assessment', '5')),
            # Get just Easy/Medium/Hard
            'feasibility': sections.get('feasibility', 'Medium').split()[0],
            'source_gap': gap.get('description', '')
        }

    def _extract_list(self, text: str) -> List[str]:
        """Extract list items from text"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                items.append(line.lstrip('-•').strip())
            # Simple list without bullets
            elif line and not line.startswith('['):
                items.append(line)
        return items[:5]  # Limit to 5 items

    def _extract_score(self, text: str) -> float:
        """Extract numerical score from text"""
        match = re.search(r'(\d+(?:\.\d+)?)', text)
        if match:
            score = float(match.group(1))
            return min(score / 10.0, 1.0)  # Normalize to 0-1
        return 0.5

    def _load_templates(self) -> Dict:
        """Load hypothesis templates for different domains"""
        return {
            'materials': "If we {action} {material} at {condition}, then {property} should {change} because {mechanism}.",
            'synthesis': "Synthesizing {material} using {method} at {parameters} should yield {property} of {value}.",
            'doping': "Doping {host_material} with {dopant} at {concentration} will {effect} due to {mechanism}.",
            'combination': "Combining {material_a} with {material_b} should create {property} enhancement via {mechanism}."
        }
