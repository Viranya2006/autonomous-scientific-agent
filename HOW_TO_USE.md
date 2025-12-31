# 🧬 Autonomous Scientific Agent - User Guide

## What Is This Application?

The **Autonomous Scientific Agent** is an AI-powered research assistant that automatically conducts scientific research in materials science. It combines multiple AI systems (Gemini, GROQ) with real scientific databases (Materials Project) to:

- **Collect** research papers from arXiv
- **Analyze** papers to find knowledge gaps
- **Generate** novel hypotheses
- **Test** hypotheses using computational methods
- **Discover** promising research directions

Think of it as a **24/7 research assistant** that can read hundreds of papers, identify gaps in knowledge, propose new experiments, and validate them computationally - all automatically!

---

## What Can It Do?

### 🔍 **Automated Literature Review**

- Searches and downloads papers from arXiv
- Reads and analyzes scientific content
- Extracts key findings and methodologies
- Identifies what's missing in current research

### 💡 **Hypothesis Generation**

- Creates testable scientific hypotheses
- Checks novelty against existing literature
- Analyzes feasibility using real data
- Prioritizes the most promising ideas

### 🧪 **Computational Testing**

- Validates hypotheses using Materials Project database
- Performs computational experiments
- Provides confidence scores for results
- Classifies outcomes as PASS/FAIL/INCONCLUSIVE

### 📊 **Beautiful Dashboard**

- Real-time visualization of research progress
- Interactive exploration of papers and hypotheses
- Charts showing novelty and feasibility distributions
- Track discoveries and experimental results

---

## How to Use This Application

### 🚀 Quick Start (3 Steps)

#### **Step 1: Configure Your API Keys**

Edit the `.env` file in the project root:

```env
# Required API Keys
GEMINI_API_KEY=your-gemini-api-key-here
GROQ_API_KEY=your-groq-api-key-here
MP_API_KEY=your-materials-project-key-here
```

**Where to get API keys:**

- **Gemini:** https://makersuite.google.com/app/apikey (Free: 1,500 requests/day)
- **GROQ:** https://console.groq.com/ (Free: 30 requests/min)
- **Materials Project:** https://next-gen.materialsproject.org/api (Free: 50,000 requests/month)

#### **Step 2: Run the Autonomous Agent**

Open PowerShell in the project directory:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the agent
python scripts/run_agent.py
```

The agent will:

1. Collect 20 research papers (2 minutes)
2. Analyze papers and find gaps (5 minutes)
3. Generate 20 novel hypotheses (6 minutes)
4. Test top 10 hypotheses (2 minutes)
5. Save all results to `data/agent_results/`

**Total time: ~15 minutes**

#### **Step 3: View Results in Dashboard**

```powershell
# Launch web dashboard
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser to explore!

---

## Dashboard Guide

### 📊 **Overview Tab**

- View summary metrics (papers collected, hypotheses generated, tests completed)
- See novelty score distribution chart
- View feasibility level breakdown
- Track test results (PASS/FAIL/INCONCLUSIVE)

### 📚 **Papers Tab**

- Browse all collected research papers
- Search papers by title, author, or content
- Sort by relevance score
- Read abstracts and key findings
- Click links to view full papers on arXiv

### 💡 **Hypotheses Tab**

- Explore all generated hypotheses
- Filter by novelty score (0-1 scale)
- Filter by feasibility level (Easy/Medium/Hard)
- Search for specific materials or methods
- View expected outcomes and metrics

### 🧪 **Experiments Tab**

- See computational test results
- Filter by outcome (PASS/FAIL/INCONCLUSIVE)
- View confidence scores
- Read AI analysis of evidence
- Understand why tests passed or failed

### 🎉 **Discoveries Tab**

- Highlights of most promising findings
- High-confidence validated hypotheses
- Evidence supporting each discovery
- Iteration tracking

---

## Customizing Your Research

### Change Research Topic

Edit `scripts/run_agent.py`:

```python
# Line 15: Change the research query
query = "your research topic here"

# Examples:
query = "perovskite solar cell stability"
query = "solid state lithium ion batteries"
query = "carbon nanotube composites"
query = "thermoelectric materials"
```

### Adjust Research Parameters

```python
# Collect more papers
max_papers = 50  # Default: 20

# Generate more hypotheses
max_hypotheses = 50  # Default: 20

# Run multiple research cycles
max_iterations = 3  # Default: 1
```

### Enable Multi-Key Rotation (Optional)

For higher throughput, add multiple API keys in `.env`:

```env
# Instead of single keys
GEMINI_API_KEY_1=first-key
GEMINI_API_KEY_2=second-key
GEMINI_API_KEY_3=third-key

GROQ_API_KEY_1=first-key
GROQ_API_KEY_2=second-key
GROQ_API_KEY_3=third-key
```

The system automatically rotates keys when hitting rate limits!

---

## Understanding the Results

### **Novelty Score (0-1)**

- **0.0-0.3:** Similar to existing research
- **0.3-0.6:** Moderately novel
- **0.6-0.8:** Highly novel ⭐
- **0.8-1.0:** Very novel ⭐⭐

### **Feasibility Score (0-1)**

- **0.0-0.3:** Difficult (limited data)
- **0.3-0.6:** Medium (some data available)
- **0.6-1.0:** Easy (abundant data) ⭐

### **Test Confidence (0-1)**

- **0.0-0.4:** Low confidence
- **0.4-0.7:** Medium confidence
- **0.7-1.0:** High confidence ⭐

### **Test Results**

- **PASS:** Hypothesis validated by computational data ✅
- **FAIL:** Hypothesis contradicted by data ❌
- **INCONCLUSIVE:** Insufficient data to determine ⚠️

---

## Example Workflow

### Scenario: Research on Battery Materials

1. **Set Research Query**

   ```python
   query = "lithium ion battery cathode materials"
   ```

2. **Run Agent**

   ```powershell
   python scripts/run_agent.py
   ```

   **Output:**

   - 20 papers collected on battery cathodes
   - 15 knowledge gaps identified
   - 20 hypotheses generated about new materials
   - 10 hypotheses tested computationally
   - 3 discoveries found with >70% confidence

3. **Explore Results**

   - Open dashboard: http://localhost:8501
   - Review papers in Papers tab
   - Check novel hypotheses in Hypotheses tab
   - See which tests passed in Experiments tab
   - Read discoveries in Discoveries tab

4. **Take Action**
   - Export promising hypotheses
   - Design real experiments based on validated ideas
   - Write research proposals using generated insights

---

## Advanced Features

### **GROQ-Only Mode**

If Gemini quota is exhausted, the system automatically uses GROQ for all operations:

```powershell
python scripts/generate_hypotheses_groq.py
```

### **API Key Rotation**

The system automatically:

- Detects multiple keys (KEY_1, KEY_2, KEY_3)
- Rotates on 429 rate limit errors
- Re-enables keys after 60 minutes
- Tracks usage per key

### **Batch Processing**

Process multiple research queries:

```python
queries = [
    "solid electrolytes",
    "perovskite stability",
    "thermoelectric materials"
]

for query in queries:
    agent = AutonomousScientist()
    agent.run(query=query, max_papers=20)
    agent.save_results(f"data/{query.replace(' ', '_')}")
```

---

## Troubleshooting

### **Problem: "API key not found"**

**Solution:** Add your API keys to the `.env` file

### **Problem: "Gemini quota exceeded"**

**Solution:**

- Use GROQ-only mode: `python scripts/generate_hypotheses_groq.py`
- Or add multiple Gemini keys (GEMINI_API_KEY_1/2/3)

### **Problem: "No papers found"**

**Solution:** Try a broader search query or check arXiv availability

### **Problem: "Dashboard won't start"**

**Solution:**

```powershell
pip install streamlit plotly
streamlit run dashboard/app.py
```

### **Problem: "Tests are INCONCLUSIVE"**

**Solution:** Materials may not be in Materials Project database. This is normal - not all materials have computational data available.

---

## Tips for Best Results

### ✅ **Do:**

- Use specific research queries ("lithium cobalt oxide batteries")
- Check novelty scores before testing hypotheses
- Focus on hypotheses with high feasibility scores
- Run during off-peak hours for faster API responses
- Save results regularly

### ❌ **Don't:**

- Use very broad queries ("materials science")
- Test too many hypotheses at once (API limits)
- Ignore feasibility scores (unfeasible = no data)
- Run without API keys configured
- Expect 100% test pass rate (some hypotheses will fail)

---

## File Structure

```
THE AUTONOMOUS SCIENTIFIC AGENT/
├── data/
│   ├── agent_results/          # Research outputs
│   ├── hypotheses_groq.csv     # Generated hypotheses
│   └── papers.csv              # Collected papers
├── dashboard/
│   └── app.py                  # Web dashboard
├── scripts/
│   ├── run_agent.py            # Main launcher
│   └── generate_hypotheses_groq.py  # GROQ-only mode
├── src/
│   ├── agent/                  # Autonomous agent
│   ├── experiments/            # Hypothesis testing
│   ├── reasoning/              # Hypothesis generation
│   ├── analysis/               # Paper analysis
│   └── api/                    # API clients
├── tests/                      # Test files
├── .env                        # Your API keys (create this!)
└── requirements.txt            # Python dependencies
```

---

## What Makes This Special?

### 🤖 **Fully Autonomous**

Once started, the agent runs the entire research cycle without human intervention.

### 🧠 **Multi-AI System**

Combines multiple AI models (Gemini 2.0 Flash, Llama 3.1 8B) for different tasks.

### 🔬 **Real Scientific Data**

Uses actual computational materials database (Materials Project) with 150,000+ materials.

### 📊 **Production Ready**

- Error handling and recovery
- API rate limit management
- Result persistence
- Comprehensive logging

### 🎨 **Beautiful Interface**

Interactive web dashboard with charts, search, and filtering.

---

## Success Metrics

Based on testing, you can expect:

| Metric               | Result              |
| -------------------- | ------------------- |
| Papers Collected     | 20 in ~2 minutes    |
| Knowledge Gaps       | 10-20 identified    |
| Hypotheses Generated | 20 in ~6 minutes    |
| Novelty Rate         | ~100% (all novel)   |
| Feasibility Rate     | ~85% (feasible)     |
| Tests Completed      | 10 in ~2 minutes    |
| Discoveries          | 2-5 promising ideas |
| Total Runtime        | ~15 minutes         |

---

## Support & Documentation

- **Complete Guide:** `PHASE4_README.md`
- **Technical Summary:** `PHASE4_COMPLETE.md`
- **Test Report:** `TEST_REPORT.md`
- **API Setup:** `.env.example`

---

## License & Credits

Built with:

- **Python 3.11**
- **Streamlit** - Web dashboard
- **Google Gemini 2.0 Flash** - Analysis & reasoning
- **GROQ (Llama 3.1)** - Hypothesis generation
- **Materials Project** - Computational validation
- **arXiv** - Paper collection

---

**Ready to discover something new? Start your autonomous research now!** 🚀🧬🤖

```powershell
python scripts/run_agent.py
```
