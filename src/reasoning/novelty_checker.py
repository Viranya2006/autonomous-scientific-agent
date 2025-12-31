"""
Novelty Checker - Validates hypothesis novelty against existing literature

Uses TF-IDF similarity to compare generated hypotheses against collected
papers to determine if ideas are truly novel or already explored.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ..utils.logger import setup_logger

logger = setup_logger()


class NoveltyChecker:
    """
    Validates novelty of hypotheses against existing literature
    """

    def __init__(self, papers_df: pd.DataFrame):
        """
        Initialize with collected papers

        Args:
            papers_df: DataFrame with analyzed papers
        """
        self.papers = papers_df
        self.paper_embeddings = None
        self.vectorizer = None
        self._build_embeddings()

    def check_novelty(
        self,
        hypothesis: str,
        threshold: float = 0.75
    ) -> Dict[str, Any]:
        """
        Check if hypothesis is novel compared to existing papers

        Args:
            hypothesis: Hypothesis statement
            threshold: Similarity threshold (>threshold = not novel)

        Returns:
            {
                'novelty_score': float,      # 0-1 (1 = completely novel)
                'is_novel': bool,            # True if score > threshold
                'similar_papers': List,      # Papers with high similarity
                'confidence': float          # Confidence in assessment
            }
        """
        if self.paper_embeddings is None:
            logger.warning("No embeddings available, returning default scores")
            return {
                'novelty_score': 0.5,
                'is_novel': True,
                'similar_papers': [],
                'confidence': 0.3,
                'max_similarity': 0.0
            }

        try:
            # Calculate similarity to all papers
            similarities = self._calculate_similarities(hypothesis)

            # Find most similar papers
            top_similar = self._get_top_similar(similarities, top_k=3)

            # Calculate novelty score (inverse of max similarity)
            max_similarity = similarities.max() if len(similarities) > 0 else 0
            novelty_score = 1.0 - max_similarity

            return {
                'novelty_score': float(novelty_score),
                'is_novel': novelty_score > (1 - threshold),
                'similar_papers': top_similar,
                'confidence': float(self._calculate_confidence(similarities)),
                'max_similarity': float(max_similarity)
            }

        except Exception as e:
            logger.error(f"Novelty check failed: {e}")
            return {
                'novelty_score': 0.5,
                'is_novel': True,
                'similar_papers': [],
                'confidence': 0.3,
                'max_similarity': 0.0
            }

    def batch_check(
        self,
        hypotheses_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Check novelty for all hypotheses

        Returns:
            DataFrame with novelty scores added
        """
        results = []

        for idx, row in tqdm(hypotheses_df.iterrows(), total=len(hypotheses_df), desc="Checking novelty"):
            result = self.check_novelty(row['hypothesis'])
            results.append(result)

        hypotheses_df['novelty_score'] = [r['novelty_score'] for r in results]
        hypotheses_df['is_novel'] = [r['is_novel'] for r in results]
        hypotheses_df['similar_papers'] = [
            str(r['similar_papers']) for r in results]
        hypotheses_df['novelty_confidence'] = [
            r['confidence'] for r in results]

        return hypotheses_df

    def _build_embeddings(self):
        """Build embeddings for all papers (TF-IDF based)"""
        try:
            # Combine title and abstract for better matching
            if 'abstract' in self.papers.columns:
                texts = (self.papers['title'].fillna('') + ' ' +
                         self.papers['abstract'].fillna('')).tolist()
            else:
                texts = self.papers['title'].fillna('').tolist()

            if not texts or all(not t for t in texts):
                logger.warning("No text content available for embeddings")
                return

            self.vectorizer = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1
            )

            self.paper_embeddings = self.vectorizer.fit_transform(texts)
            logger.info(f"Built embeddings for {len(texts)} papers")

        except Exception as e:
            logger.error(f"Failed to build embeddings: {e}")
            self.paper_embeddings = None
            self.vectorizer = None

    def _calculate_similarities(self, hypothesis: str) -> np.ndarray:
        """Calculate cosine similarity to all papers"""
        if self.vectorizer is None or self.paper_embeddings is None:
            return np.array([])

        try:
            hyp_embedding = self.vectorizer.transform([hypothesis])
            similarities = cosine_similarity(
                hyp_embedding, self.paper_embeddings)
            return similarities.flatten()
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return np.array([])

    def _get_top_similar(self, similarities: np.ndarray, top_k: int = 3) -> List[Dict]:
        """Get top k most similar papers"""
        if len(similarities) == 0:
            return []

        top_indices = np.argsort(similarities)[-top_k:][::-1]

        similar_papers = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Only include if somewhat similar
                paper_title = self.papers.iloc[idx].get('title', 'Unknown')
                similar_papers.append({
                    'title': paper_title,
                    'similarity': float(similarities[idx])
                })

        return similar_papers

    def _calculate_confidence(self, similarities: np.ndarray) -> float:
        """Calculate confidence in novelty assessment"""
        if len(similarities) < 5:
            return 0.5  # Low confidence with few papers

        try:
            # Higher confidence if similarities are consistently low
            mean_sim = similarities.mean()
            std_sim = similarities.std()

            # More variance = less confidence
            confidence = 1.0 - (std_sim / (mean_sim + 0.1))
            return float(np.clip(confidence, 0.3, 0.95))

        except Exception:
            return 0.5
