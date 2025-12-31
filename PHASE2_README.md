# Phase 2: Paper Collection & AI-Powered Analysis

## 🎯 Overview

Phase 2 transforms your Autonomous Scientific Agent into a **research intelligence system** that:

1. **Collects** scientific papers from arXiv
2. **Analyzes** them using dual AI (Gemini + GROQ)
3. **Extracts** knowledge into structured graphs
4. **Identifies** research gaps automatically
5. **Generates** testable research hypotheses

## 🚀 Quick Start

### 1. Setup GROQ API Key

Get your free GROQ API key:

1. Visit https://console.groq.com/
2. Sign up/login
3. Create a new API key

Add to your `.env` file:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Install Additional Dependencies

```bash
# Activate your virtual environment first
.\venv\Scripts\Activate

# Install new packages
pip install networkx matplotlib seaborn jupyter
```

### 3. Run Your First Analysis

```bash
python scripts/collect_and_analyze.py \
    --query "graphene thermal conductivity" \
    --max-papers 50 \
    --days 30
```

## 📊 What Gets Generated

The pipeline creates comprehensive outputs in `data/results/`:

### 1. Paper Collection

- `*_papers.json` - Structured paper data
- `*_papers.csv` - Spreadsheet view of papers

### 2. AI Analysis

- `*_analyses.json` - Complete AI analyses
- `*_summary.csv` - Quick overview of all papers

### 3. Knowledge Extraction

- `*_knowledge_graph.graphml` - Network graph of entities
- `*_patterns.json` - Frequent patterns discovered

### 4. Research Intelligence

- `*_gaps.json` - Identified research gaps
- `*_hypotheses.json` - AI-generated hypotheses
- `*_SUMMARY.json` - Pipeline summary report

## 🔬 Pipeline Details

### Stage 1: Paper Collection (ArXivCollector)

Searches arXiv with powerful filters:

```python
from src.data_collection import ArXivCollector

collector = ArXivCollector()
papers = collector.search_recent(
    query="2D materials electronic properties",
    days=30,
    max_results=100,
    categories=["cond-mat.mtrl-sci", "cond-mat.mes-hall"]
)
```

**Features:**

- Smart rate limiting (respects arXiv API limits)
- Category filtering (materials science, physics, etc.)
- Date range filtering
- Automatic caching
- CSV/JSON export

### Stage 2: AI-Powered Analysis (PaperAnalyzer)

Dual AI system for comprehensive analysis:

**GROQ (Llama 3.1 8B)** - Fast entity extraction:

- Materials mentioned
- Properties studied
- Methods used
- Applications
- Performance metrics

**Gemini (2.5-flash)** - Deep insights:

- Key findings (quantitative when possible)
- Research significance assessment
- Novelty evaluation
- Limitations identified
- Future research directions

**Output Example:**

```python
{
    "arxiv_id": "2401.12345",
    "title": "High Thermal Conductivity in Graphene...",
    "materials": ["graphene", "h-BN", "MoS2"],
    "properties": ["thermal conductivity", "phonon transport"],
    "methods": ["DFT", "molecular dynamics", "Raman spectroscopy"],
    "key_findings": [
        "Achieved 5000 W/mK thermal conductivity",
        "Phonon mean free path exceeds 1 μm"
    ],
    "research_significance": "...",
    "novelty_assessment": "...",
    "relevance_score": 8.5,
    "research_type": "computational"
}
```

### Stage 3: Knowledge Extraction (KnowledgeExtractor)

Builds structured knowledge graphs using NetworkX:

**Graph Structure:**

- **Nodes:** Materials, properties, methods
- **Edges:** Relationships ("has_property", "studies")
- **Attributes:** Frequency, supporting papers

**Pattern Discovery:**

- Most studied materials
- Common property measurements
- Frequent method combinations
- Material-property co-occurrences

**Example Query:**

```python
extractor = KnowledgeExtractor()
graph = extractor.build_knowledge_graph(analyses)

# Find all properties studied for graphene
graphene_properties = list(graph.neighbors("graphene"))
```

### Stage 4: Gap Identification

AI identifies understudied areas by:

1. **Graph Analysis:** Finding material-property combinations with low coverage
2. **Methodological Gaps:** Identifying underrepresented research approaches
3. **AI Validation:** Using Gemini to assess scientific merit of potential gaps

**Output Example:**

```json
{
  "gap_id": "gap_1",
  "description": "Thermal conductivity of transition metal dichalcogenides at cryogenic temperatures remains largely unexplored...",
  "related_materials": ["MoS2", "WSe2"],
  "related_properties": ["thermal conductivity", "low-temperature transport"],
  "confidence": 0.85,
  "priority": "high"
}
```

### Stage 5: Hypothesis Generation

Gemini generates specific, testable hypotheses:

**Input:** Research gaps + Paper analyses
**Output:** Actionable research proposals

**Example:**

```json
{
  "hypothesis_id": "gap_1_hyp_1",
  "statement": "MoS2 monolayers will exhibit anomalous thermal conductivity enhancement below 50K due to reduced phonon-phonon scattering",
  "rationale": "Recent studies show...",
  "materials_involved": ["MoS2", "WSe2"],
  "properties_involved": ["thermal conductivity", "phonon lifetime"],
  "suggested_methods": [
    "ultralow temperature measurements",
    "DFT phonon calculations"
  ],
  "feasibility": "high",
  "novelty_score": 8.5
}
```

## 🎛️ Command-Line Options

Full pipeline options:

```bash
python scripts/collect_and_analyze.py \
    --query "machine learning materials discovery" \
    --max-papers 100 \
    --days 60 \
    --categories cond-mat.mtrl-sci physics.comp-ph \
    --max-analyze 50 \
    --min-relevance 6.0 \
    --min-gap-confidence 0.7 \
    --max-hypotheses 15 \
    --output-dir data/results \
    --log-level INFO
```

### Key Parameters:

- `--query`: Search keywords (required)
- `--max-papers`: Papers to collect (default: 50)
- `--days`: Search recent papers from last N days (default: 30)
- `--categories`: arXiv categories to search
- `--max-analyze`: Limit analyses (saves API costs)
- `--min-relevance`: Filter low-relevance papers (0-10 scale)
- `--min-gap-confidence`: Gap quality threshold (0-1)
- `--max-hypotheses`: Number of hypotheses to generate

### Efficient Usage:

```bash
# Quick test (cheap, fast)
python scripts/collect_and_analyze.py \
    --query "your topic" \
    --max-papers 10 \
    --max-analyze 5

# Production run (comprehensive)
python scripts/collect_and_analyze.py \
    --query "your topic" \
    --max-papers 200 \
    --min-relevance 6.0
```

## 📓 Interactive Exploration

Use the Jupyter notebook for deep dives:

```bash
jupyter notebook notebooks/02_phase2_exploration.ipynb
```

**Notebook Sections:**

1. Load pipeline results
2. Visualize paper statistics
3. Explore AI analyses
4. Interactive knowledge graph
5. Research patterns
6. Gap analysis
7. Hypothesis evaluation
8. Custom queries

## 🧪 Testing

Run Phase 2 tests:

```bash
# All tests
pytest tests/test_phase2.py -v

# Specific test class
pytest tests/test_phase2.py::TestPaperAnalyzer -v

# Quick smoke test
pytest tests/test_phase2.py::TestArXivCollector::test_basic_search -v
```

## 💡 Example Workflows

### Workflow 1: Materials Discovery

```bash
# Find recent work on novel 2D materials
python scripts/collect_and_analyze.py \
    --query "novel 2D materials beyond graphene" \
    --max-papers 100 \
    --days 90 \
    --min-relevance 7.0
```

### Workflow 2: Property Investigation

```bash
# Study thermal transport in nanomaterials
python scripts/collect_and_analyze.py \
    --query "thermal transport nanomaterials phonons" \
    --categories cond-mat.mtrl-sci cond-mat.mes-hall \
    --max-papers 150
```

### Workflow 3: Method Survey

```bash
# Track machine learning in materials
python scripts/collect_and_analyze.py \
    --query "machine learning materials prediction" \
    --max-papers 200 \
    --days 180
```

## 📈 Cost Estimates

### API Usage (per 50 papers analyzed):

**GROQ (Free tier: 30 req/min, generous limits):**

- Entity extraction: ~50 requests
- Classification: ~100 requests
- Total: ~150 requests (~$0.00)

**Gemini (Free tier: 1500 requests/day):**

- Deep analysis: ~50 requests
- Gap assessment: ~10 requests
- Hypothesis generation: ~5 requests
- Total: ~65 requests (~$0.00)

**Both APIs have generous free tiers sufficient for research use!**

### Time Estimates:

- Paper collection: 10-30 seconds
- Analysis (50 papers): 10-15 minutes
- Knowledge extraction: 1-2 minutes
- Gap identification: 2-3 minutes
- Hypothesis generation: 1-2 minutes

**Total: ~15-20 minutes for 50 papers**

## 🔧 Programmatic Usage

Use modules in your own scripts:

```python
from src.data_collection import ArXivCollector, search_materials_papers
from src.analysis import PaperAnalyzer, KnowledgeExtractor

# Collect papers
papers = search_materials_papers(
    materials=["graphene", "MoS2"],
    properties=["thermal conductivity"],
    max_results=50
)

# Analyze with AI
analyzer = PaperAnalyzer()
analyses = analyzer.analyze_batch(papers)

# Extract knowledge
extractor = KnowledgeExtractor()
graph = extractor.build_knowledge_graph(analyses)
gaps = extractor.identify_research_gaps(analyses)
hypotheses = extractor.generate_hypotheses(gaps, analyses)

# Save results
analyzer.save_analyses(analyses, "my_analyses")
extractor.save_knowledge_graph("my_graph")
```

## 🎯 Research Applications

### 1. Literature Review Automation

Analyze 200+ papers in 30 minutes instead of weeks

### 2. Research Gap Discovery

Systematically identify unexplored areas

### 3. Hypothesis Generation

Get AI-powered research ideas based on current knowledge

### 4. Trend Analysis

Track emerging materials, properties, and methods

### 5. Collaboration Discovery

Find researchers working on related topics

## 🛠️ Troubleshooting

### "GROQ_API_KEY not set"

Add your key to `.env` file. Get it from https://console.groq.com/

### "No papers found"

- Try broader query terms
- Increase `--days` parameter
- Remove category filters
- Check arXiv.org to verify papers exist

### "Analysis taking too long"

- Reduce `--max-analyze`
- Use `--skip-collection` to reuse existing papers
- Check your internet connection

### Import errors

```bash
pip install networkx matplotlib seaborn jupyter pandas requests
```

### Rate limit errors

The system has built-in rate limiting. If you hit limits:

- Wait a few minutes
- Reduce `--max-papers`
- Check your API quota at provider websites

## 📚 Additional Resources

- **arXiv API:** https://arxiv.org/help/api
- **GROQ Docs:** https://console.groq.com/docs
- **Gemini API:** https://ai.google.dev/
- **NetworkX:** https://networkx.org/documentation/stable/

## 🚀 Next Steps

After Phase 2, you can:

1. **Integrate with Materials Project** - Combine paper insights with materials database
2. **Automated Experiments** - Use hypotheses to guide simulations
3. **Continuous Monitoring** - Schedule daily paper collection
4. **Custom Analysis** - Add domain-specific entity extractors
5. **Export Reports** - Generate LaTeX/PDF literature reviews

## 💬 Support

Having issues? Check:

1. This README
2. Test files in `tests/test_phase2.py` for examples
3. Docstrings in source code
4. Example notebook for interactive debugging

---

**Phase 2 Complete! Your agent is now a research intelligence system.** 🎉
