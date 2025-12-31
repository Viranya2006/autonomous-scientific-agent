"""
ArXiv Paper Collector for Autonomous Scientific Agent.

This module provides functionality to search and collect scientific papers
from arXiv.org based on keywords, date ranges, and categories.
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
import pandas as pd
from loguru import logger

from ..utils.rate_limiter import RateLimiter


@dataclass
class Paper:
    """Represents a scientific paper from arXiv."""

    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    updated_date: str
    pdf_url: str
    arxiv_url: str
    primary_category: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """Create paper from dictionary."""
        return cls(**data)


class ArXivCollector:
    """
    Collect papers from arXiv API.

    Searches arXiv for papers matching specified criteria and returns
    structured paper data including metadata and abstracts.
    """

    BASE_URL = "http://export.arxiv.org/api/query"
    NAMESPACE = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }

    def __init__(
        self,
        rate_limit: float = 0.33,  # arXiv allows ~3 requests per second
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize ArXiv collector.

        Args:
            rate_limit: Maximum requests per second (default: 0.33 = 3 req/sec)
            cache_dir: Directory to cache results (default: data/papers/)
        """
        self.rate_limiter = RateLimiter(calls_per_second=rate_limit)

        if cache_dir is None:
            cache_dir = Path(__file__).resolve().parents[2] / "data" / "papers"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"Initialized ArXiv collector with cache at: {self.cache_dir}")

    def search(
        self,
        query: str,
        max_results: int = 100,
        start: int = 0,
        sort_by: str = "relevance",
        sort_order: str = "descending",
        categories: Optional[List[str]] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Paper]:
        """
        Search arXiv for papers matching query.

        Args:
            query: Search query (supports arXiv query syntax)
            max_results: Maximum number of results to return
            start: Starting index for pagination
            sort_by: Sort criteria ("relevance", "lastUpdatedDate", "submittedDate")
            sort_order: Sort order ("ascending", "descending")
            categories: Filter by arXiv categories (e.g., ["cond-mat.mtrl-sci"])
            date_from: Filter papers published after this date (YYYY-MM-DD)
            date_to: Filter papers published before this date (YYYY-MM-DD)

        Returns:
            List of Paper objects matching criteria

        Example:
            >>> collector = ArXivCollector()
            >>> papers = collector.search(
            ...     query="thermal conductivity graphene",
            ...     max_results=50,
            ...     categories=["cond-mat.mtrl-sci"]
            ... )
        """
        self.rate_limiter.wait_if_needed()

        # Build query with category filters
        full_query = query
        if categories:
            category_filters = " OR ".join(f"cat:{cat}" for cat in categories)
            full_query = f"({query}) AND ({category_filters})"

        # Build API request parameters
        params = {
            "search_query": full_query,
            "start": start,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

        logger.info(
            f"Searching arXiv: query='{query}', max_results={max_results}")
        logger.debug(f"Full query: {full_query}")

        try:
            # Make request
            with urllib.request.urlopen(url, timeout=30) as response:
                xml_data = response.read().decode('utf-8')

            # Parse XML response
            root = ET.fromstring(xml_data)

            # Extract papers from response
            papers = []
            for entry in root.findall("atom:entry", self.NAMESPACE):
                try:
                    paper = self._parse_entry(entry)

                    # Apply date filters if specified
                    if date_from or date_to:
                        pub_date = datetime.fromisoformat(
                            paper.published_date.replace('Z', '+00:00'))

                        if date_from:
                            # Make filter_from timezone-aware
                            filter_from = datetime.fromisoformat(date_from)
                            if filter_from.tzinfo is None:
                                from datetime import timezone
                                filter_from = filter_from.replace(
                                    tzinfo=timezone.utc)
                            if pub_date < filter_from:
                                continue

                        if date_to:
                            # Make filter_to timezone-aware
                            filter_to = datetime.fromisoformat(date_to)
                            if filter_to.tzinfo is None:
                                from datetime import timezone
                                filter_to = filter_to.replace(
                                    tzinfo=timezone.utc)
                            if pub_date > filter_to:
                                continue

                    papers.append(paper)

                except Exception as e:
                    logger.warning(f"Failed to parse paper entry: {e}")
                    continue

            logger.info(f"Found {len(papers)} papers matching criteria")
            return papers

        except Exception as e:
            logger.error(f"ArXiv search failed: {e}")
            raise

    def _parse_entry(self, entry: ET.Element) -> Paper:
        """Parse XML entry into Paper object."""
        ns = self.NAMESPACE

        # Extract arXiv ID from the id URL
        id_elem = entry.find("atom:id", ns)
        if id_elem is None or id_elem.text is None:
            raise ValueError("Entry missing required id element")
        id_url = id_elem.text
        arxiv_id = id_url.split("/abs/")[-1]

        # Extract title and clean whitespace
        title_elem = entry.find("atom:title", ns)
        if title_elem is None or title_elem.text is None:
            raise ValueError("Entry missing required title element")
        title = title_elem.text
        title = " ".join(title.split())  # Normalize whitespace

        # Extract authors
        authors = []
        for author in entry.findall("atom:author", ns):
            name_elem = author.find("atom:name", ns)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text)

        # Extract abstract and clean whitespace
        abstract_elem = entry.find("atom:summary", ns)
        if abstract_elem is None or abstract_elem.text is None:
            abstract = ""
        else:
            abstract = abstract_elem.text
            abstract = " ".join(abstract.split())  # Normalize whitespace

        # Extract categories
        categories = []
        for cat in entry.findall("atom:category", ns):
            term = cat.get("term")
            if term:
                categories.append(term)

        # Extract primary category (using arxiv namespace)
        primary_cat_elem = entry.find("arxiv:primary_category", ns)
        if primary_cat_elem is not None:
            primary_category = primary_cat_elem.get("term")
        elif categories:
            primary_category = categories[0]  # Fallback to first category
        else:
            primary_category = "unknown"

        # Extract dates
        published_elem = entry.find("atom:published", ns)
        updated_elem = entry.find("atom:updated", ns)

        published = published_elem.text if published_elem is not None else ""
        updated = updated_elem.text if updated_elem is not None else published

        # Build URLs
        pdf_url = id_url.replace("/abs/", "/pdf/") + ".pdf"
        arxiv_url = id_url

        return Paper(
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            categories=categories,
            published_date=published,
            updated_date=updated,
            pdf_url=pdf_url,
            arxiv_url=arxiv_url,
            primary_category=primary_category
        )

    def search_recent(
        self,
        query: str,
        days: int = 7,
        max_results: int = 100,
        categories: Optional[List[str]] = None
    ) -> List[Paper]:
        """
        Search for recent papers from the last N days.

        Args:
            query: Search query
            days: Number of days to look back
            max_results: Maximum results
            categories: Category filters

        Returns:
            List of recent papers
        """
        date_from = (datetime.now() - timedelta(days=days)
                     ).strftime("%Y-%m-%d")

        return self.search(
            query=query,
            max_results=max_results,
            categories=categories,
            date_from=date_from,
            sort_by="submittedDate",
            sort_order="descending"
        )

    def save_papers(
        self,
        papers: List[Paper],
        filename: str,
        format: str = "json"
    ) -> Path:
        """
        Save papers to file.

        Args:
            papers: List of Paper objects
            filename: Output filename (without extension)
            format: Output format ("json" or "csv")

        Returns:
            Path to saved file
        """
        if format == "json":
            filepath = self.cache_dir / f"{filename}.json"
            data = [p.to_dict() for p in papers]
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format == "csv":
            filepath = self.cache_dir / f"{filename}.csv"
            df = pd.DataFrame([p.to_dict() for p in papers])
            df.to_csv(filepath, index=False, encoding='utf-8')

        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Saved {len(papers)} papers to: {filepath}")
        return filepath

    def load_papers(self, filename: str) -> List[Paper]:
        """
        Load papers from JSON file.

        Args:
            filename: JSON filename (with or without .json extension)

        Returns:
            List of Paper objects
        """
        if not filename.endswith('.json'):
            filename += '.json'

        filepath = self.cache_dir / filename

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        papers = [Paper.from_dict(p) for p in data]
        logger.info(f"Loaded {len(papers)} papers from: {filepath}")
        return papers

    def get_papers_dataframe(self, papers: List[Paper]) -> pd.DataFrame:
        """
        Convert papers to pandas DataFrame for analysis.

        Args:
            papers: List of Paper objects

        Returns:
            DataFrame with paper data
        """
        data = [p.to_dict() for p in papers]
        df = pd.DataFrame(data)

        # Convert date strings to datetime
        df['published_date'] = pd.to_datetime(df['published_date'])
        df['updated_date'] = pd.to_datetime(df['updated_date'])

        return df


def search_materials_papers(
    materials: List[str],
    properties: Optional[List[str]] = None,
    max_results: int = 100,
    days: int = 30
) -> List[Paper]:
    """
    Convenience function to search for materials science papers.

    Args:
        materials: List of material names to search for
        properties: Optional list of properties to include in search
        max_results: Maximum results
        days: Search papers from last N days

    Returns:
        List of relevant papers

    Example:
        >>> papers = search_materials_papers(
        ...     materials=["graphene", "MoS2"],
        ...     properties=["thermal conductivity", "electronic structure"],
        ...     max_results=50
        ... )
    """
    collector = ArXivCollector()

    # Build query
    material_query = " OR ".join(f'"{mat}"' for mat in materials)

    if properties:
        property_query = " OR ".join(f'"{prop}"' for prop in properties)
        query = f"({material_query}) AND ({property_query})"
    else:
        query = material_query

    # Search in materials science categories
    categories = [
        "cond-mat.mtrl-sci",  # Materials Science
        "cond-mat.mes-hall",  # Mesoscale and Nanoscale Physics
        "physics.comp-ph",    # Computational Physics
    ]

    return collector.search_recent(
        query=query,
        days=days,
        max_results=max_results,
        categories=categories
    )


if __name__ == "__main__":
    from ..utils.logger import setup_logger

    setup_logger()

    logger.info("Testing ArXiv Collector...")

    # Test 1: Basic search
    logger.info("\n=== Test 1: Basic Search ===")
    collector = ArXivCollector()
    papers = collector.search(
        query="graphene thermal conductivity",
        max_results=5,
        categories=["cond-mat.mtrl-sci"]
    )

    for i, paper in enumerate(papers, 1):
        logger.info(f"\n{i}. {paper.title}")
        logger.info(f"   Authors: {', '.join(paper.authors[:3])}...")
        logger.info(f"   Published: {paper.published_date}")
        logger.info(f"   Categories: {', '.join(paper.categories)}")
        logger.info(f"   Abstract: {paper.abstract[:200]}...")

    # Test 2: Recent papers
    logger.info("\n=== Test 2: Recent Papers ===")
    recent = collector.search_recent(
        query="machine learning materials",
        days=7,
        max_results=3
    )
    logger.info(f"Found {len(recent)} recent papers")

    # Test 3: Save and load
    logger.info("\n=== Test 3: Save/Load ===")
    filepath = collector.save_papers(papers, "test_papers", format="json")
    loaded = collector.load_papers("test_papers")
    logger.info(f"Saved and loaded {len(loaded)} papers")

    # Test 4: DataFrame conversion
    logger.info("\n=== Test 4: DataFrame ===")
    df = collector.get_papers_dataframe(papers)
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")

    logger.info("\n✨ ArXiv Collector tests completed!")
