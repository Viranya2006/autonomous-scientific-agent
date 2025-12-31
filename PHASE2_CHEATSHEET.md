# Phase 2 Command Cheatsheet

## 🚀 Essential Commands

### First Time Setup

```bash
# Add GROQ API key to .env
GROQ_API_KEY=gsk_your_key_here

# Install Phase 2 packages
pip install networkx matplotlib seaborn jupyter

# Verify setup
python scripts/setup_phase2.py
```

### Run Analysis Pipeline

```bash
# Basic (50 papers, ~15 min)
python scripts/collect_and_analyze.py --query "your topic" --max-papers 50

# Quick test (10 papers, ~3 min)
python scripts/collect_and_analyze.py --query "test" --max-papers 10

# Comprehensive (200 papers, ~1 hour)
python scripts/collect_and_analyze.py --query "your topic" --max-papers 200 --min-relevance 6.0
```

### Explore Results

```bash
# Interactive notebook
jupyter notebook notebooks/02_phase2_exploration.ipynb

# List available results
ls data/results/*_SUMMARY.json
```

### Run Tests

```bash
pytest tests/test_phase2.py -v
```

## 📊 Common Workflows

### Materials Discovery

```bash
python scripts/collect_and_analyze.py \
    --query "novel 2D materials beyond graphene" \
    --max-papers 100 \
    --categories cond-mat.mtrl-sci cond-mat.mes-hall
```

### Recent Work (Last 2 Weeks)

```bash
python scripts/collect_and_analyze.py \
    --query "perovskite solar cells" \
    --days 14 \
    --max-papers 50
```

### High-Quality Papers Only

```bash
python scripts/collect_and_analyze.py \
    --query "topological insulators" \
    --max-papers 150 \
    --min-relevance 7.0
```

## 🎯 Quick Parameter Guide

| Flag              | Example             | Purpose                 |
| ----------------- | ------------------- | ----------------------- |
| `--query`         | `"graphene"`        | Search terms (required) |
| `--max-papers`    | `50`                | Papers to collect       |
| `--days`          | `30`                | Last N days             |
| `--max-analyze`   | `20`                | Limit analyses          |
| `--min-relevance` | `6.0`               | Filter 0-10             |
| `--categories`    | `cond-mat.mtrl-sci` | arXiv filters           |

## 📁 Output Files

All saved to `data/results/`:

- `*_papers.json` - Paper data
- `*_analyses.json` - AI analyses
- `*_gaps.json` - Research gaps
- `*_hypotheses.json` - AI ideas
- `*_SUMMARY.json` - Overview

## 🔧 Troubleshooting

```bash
# Missing API key
echo "GROQ_API_KEY=your_key" >> .env

# Missing packages
pip install networkx matplotlib seaborn jupyter

# No papers found
# → Use broader query or increase --days

# Too slow
# → Reduce --max-papers and --max-analyze
```

## 💡 Pro Tips

1. Start with 10-20 papers for testing
2. Use `--min-relevance 6.0` to filter noise
3. Results are cached - rerun safely
4. Check CSV files for quick viewing
5. Notebook has best visualizations

---

**Full docs:** `PHASE2_README.md` | **Examples:** `notebooks/02_phase2_exploration.ipynb`
