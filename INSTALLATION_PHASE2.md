# 🚀 PHASE 2 - FIRST TIME INSTALLATION

## Follow These Steps in Order

### Step 1: Get Your GROQ API Key (2 minutes)

1. Visit: https://console.groq.com/
2. Sign up with your email or GitHub
3. Navigate to "API Keys"
4. Click "Create API Key"
5. Copy the key (starts with `gsk_`)

### Step 2: Add API Key to .env File

Open `.env` file and add your GROQ key:

```bash
# Find this line in .env:
GROQ_API_KEY=your_groq_key_here

# Replace with your actual key:
GROQ_API_KEY=gsk_abc123your_actual_key_here
```

**Save the file!**

### Step 3: Install Phase 2 Dependencies

Open PowerShell in the project directory and run:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate

# Install Phase 2 packages
pip install networkx matplotlib seaborn jupyter ipykernel pytest

# Verify installation
python -c "import networkx, matplotlib, seaborn; print('✅ All packages installed!')"
```

Expected output: `✅ All packages installed!`

### Step 4: Verify Setup

```powershell
python scripts\setup_phase2.py
```

**Follow the prompts:**

- Test API connections? → Type `y` and press Enter
- Run demo? → Type `y` and press Enter

**You should see:**

- ✅ Gemini API connection successful
- ✅ GROQ API connection successful
- Papers collected and analyzed
- ✨ Demo completed successfully!

### Step 5: Run Your First Real Analysis

```powershell
python scripts\collect_and_analyze.py --query "graphene thermal conductivity" --max-papers 10
```

**This will:**

1. Collect 10 papers from arXiv (~10 seconds)
2. Analyze them with AI (~3 minutes)
3. Build knowledge graph (~30 seconds)
4. Identify research gaps (~1 minute)
5. Generate hypotheses (~1 minute)

**Total time: ~6 minutes**

**Results saved to:** `data\results\`

### Step 6: Explore Results Interactively

```powershell
jupyter notebook notebooks\02_phase2_exploration.ipynb
```

**Your browser will open with the notebook. Run all cells to see:**

- Paper statistics and timelines
- Relevance score distributions
- Knowledge graph visualization
- Research patterns
- Identified gaps and hypotheses

---

## 🎯 You're All Set!

### Quick Commands

**Analyze papers:**

```powershell
python scripts\collect_and_analyze.py --query "your topic" --max-papers 50
```

**Explore results:**

```powershell
jupyter notebook notebooks\02_phase2_exploration.ipynb
```

**Run tests:**

```powershell
pytest tests\test_phase2.py -v
```

---

## ⚠️ Troubleshooting

### "GROQ_API_KEY not set"

**Fix:** Add your key to `.env` file (see Step 2 above)

### "Import matplotlib could not be resolved"

**Fix:** Install packages (see Step 3 above)

### "No papers found"

**Fix:**

- Use broader search terms
- Check your internet connection
- Verify arXiv.org is accessible

### "API connection failed"

**Fix:**

- Verify API key in `.env` is correct
- Check internet connection
- Try again (sometimes APIs are temporarily down)

---

## 📚 Next Steps

1. ✅ Read: `PHASE2_README.md` (comprehensive guide)
2. ✅ Check: `PHASE2_CHEATSHEET.md` (quick commands)
3. ✅ Explore: Jupyter notebook (interactive)
4. ✅ Experiment: Try different queries and parameters

---

## 💡 Tips for Success

**Start Small:**

- Test with 10-20 papers first
- Then scale up to 100+

**Use Good Queries:**

- Be specific: "graphene thermal conductivity" ✅
- Avoid too broad: "materials" ❌

**Filter Results:**

- Use `--min-relevance 6.0` to get quality papers
- Use `--days 30` for recent work

**Save Costs:**

- Use `--max-analyze` to limit analyses
- Results are cached - safe to rerun

---

## ✨ Expected Behavior

**Running pipeline should show:**

```
================================================================================
AUTONOMOUS SCIENTIFIC AGENT - Phase 2 Pipeline
================================================================================
Query: graphene thermal conductivity
Max papers: 10
Output: data/results
================================================================================

📚 STEP 1: Collecting papers from arXiv...
✅ Collected 10 papers

🤖 STEP 2: Analyzing papers with AI...
  [1/10] High Thermal Conductivity... (relevance: 8.5/10)
  [2/10] Graphene-based Heat Transfer... (relevance: 7.2/10)
  ...
✅ Analyzed 10 papers

🧠 STEP 3: Building knowledge graph...
  Nodes: 45 (15 materials, 20 properties, 10 methods)
  Edges: 120
✅ Knowledge graph built

🎯 STEP 4: Identifying research gaps...
✅ Identified 5 research gaps

💡 STEP 5: Generating research hypotheses...
✅ Generated 10 hypotheses

================================================================================
✨ PIPELINE COMPLETE!
================================================================================
Papers collected: 10
Papers analyzed: 10
Knowledge graph: 45 nodes, 120 edges
Research gaps: 5
Hypotheses: 10

All results saved to: data\results
================================================================================
```

---

## 🎉 You're Ready!

**Phase 2 is now fully operational.**

Your agent can analyze hundreds of papers, build knowledge graphs, find research gaps, and generate hypotheses - all automatically.

**Happy researching! 🚀**
