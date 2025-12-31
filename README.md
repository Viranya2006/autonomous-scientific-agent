# 🧬 Autonomous Scientific Agent

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)

An AI-powered autonomous research assistant that conducts scientific research in materials science. Combines multiple AI systems (Gemini, GROQ) with real scientific databases (Materials Project) to automatically collect papers, analyze gaps, generate hypotheses, and validate them computationally.

## ✨ Features

- 🔍 **Automated Literature Review** - Searches and analyzes research papers from arXiv
- 💡 **Hypothesis Generation** - Creates novel, testable scientific hypotheses
- 🧪 **Computational Testing** - Validates hypotheses using Materials Project database
- 📊 **Beautiful Dashboard** - Interactive web interface with real-time visualizations
- 🔄 **API Key Rotation** - Automatic failover for high throughput (3 keys per service)
- 🤖 **Fully Autonomous** - Runs complete research cycles without human intervention

## 🚀 Quick Start

### **1. Clone the Repository**

```bash
git clone https://github.com/Viranya2006/autonomous-scientific-agent.git
cd autonomous-scientific-agent
```

### **2. Install Dependencies**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### **3. Configure API Keys**

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
MP_API_KEY=your-materials-project-key
```

**Get API Keys (All Free):**

- **Gemini:** https://makersuite.google.com/app/apikey (1,500 requests/day)
- **GROQ:** https://console.groq.com/ (30 requests/min)
- **Materials Project:** https://next-gen.materialsproject.org/api (50,000 requests/month)

### **4. Run the Agent**

```bash
python scripts/run_agent.py
```

Expected output: 20 papers collected, 20 hypotheses generated, 10 tests completed (~15 minutes)

### **5. View Dashboard**

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser

## 📖 Documentation

- **[How to Use](HOW_TO_USE.md)** - Complete user guide with examples
- **[Phase 4 README](PHASE4_README.md)** - Technical documentation
- **[API Setup Guide](API_SETUP_GUIDE.md)** - Detailed API configuration
- **[Contributing](CONTRIBUTING.md)** - How to contribute

## 🎯 What It Does

```
📚 Collect Papers → 🤖 Analyze Gaps → 💡 Generate Hypotheses → 🧪 Test → 🎉 Discover
```

### Example Result

**Input:** "lithium ion battery cathode materials"

**Output:**

- 20 relevant papers analyzed
- 15 knowledge gaps identified
- 20 novel hypotheses (100% novelty rate)
- 10 hypotheses tested (85% feasibility)
- 3-5 promising discoveries

## 🛠️ Technology Stack

- **Python 3.11+** - Core language
- **Streamlit** - Web dashboard
- **Google Gemini 2.0 Flash** - Analysis & reasoning
- **GROQ (Llama 3.1 8B)** - Hypothesis generation
- **Materials Project API** - Computational validation
- **arXiv API** - Paper collection
- **Plotly** - Visualizations
- **scikit-learn** - Novelty checking

## 📊 Dashboard

Interactive web interface with 5 tabs:

1. **Overview** - Research metrics and charts
2. **Papers** - Browse collected papers
3. **Hypotheses** - Explore hypotheses with novelty scores
4. **Experiments** - View test results
5. **Discoveries** - Validated findings

## 🔧 Customization

Edit `scripts/run_agent.py`:

# Mac/Linux

source venv/bin/activate

````

### **3. Get API Keys** (15 minutes)

Follow the comprehensive guide: **[API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)**

You'll need:

- 🔑 Google Gemini API key (5 min)
- 🔑 Hugging Face token (3 min)
- 🔑 Materials Project API key (5 min)

### **4. Configure .env File**

```bash
# Copy template
cp .env.example .env

# Edit with your favorite editor
notepad .env  # Windows
nano .env     # Linux/Mac

# Add your API keys:
GEMINI_API_KEY=your_actual_key_here
HF_TOKEN=your_actual_token_here
MP_API_KEY=your_actual_key_here
````

### **5. Test Everything**

```powershell
# Verify all APIs work
python scripts/test_all_apis.py

# Expected output:
# ✅ PASS | Gemini API
# ✅ PASS | Materials Project API
# ⚠️  FAIL | Hugging Face API (optional - requires paid subscription)
```

**Note:** HuggingFace deprecated their free inference API in Dec 2024. The agent works perfectly with just Gemini + Materials Project. See `HUGGINGFACE_STATUS.md` for details and alternatives.

---

## 📁 Project Structure

```
autonomous-scientist/
├── 📄 README.md                    # You are here!
├── 📄 API_SETUP_GUIDE.md          # Detailed API key instructions
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # API key template
│
├── 📂 src/                         # Source code
│   ├── config/
│   │   └── settings.py            # Configuration management
│   ├── api/
│   │   ├── gemini_client.py       # Google Gemini wrapper
│   │   ├── huggingface_client.py  # Hugging Face wrapper
│   │   └── materials_project_client.py  # Materials API wrapper
│   ├── utils/
│   │   ├── logger.py              # Logging system
│   │   └── helpers.py             # Utility functions
│   └── core/                      # Agent logic (Phase 2+)
│
├── 📂 scripts/                     # Automation scripts
│   ├── setup_project.py           # One-command setup
│   └── test_all_apis.py           # API testing suite
│
├── 📂 data/                        # Data storage
│   ├── papers/                    # Downloaded papers
│   ├── results/                   # Research outputs
│   └── cache/                     # API response cache
│
├── 📂 tests/                       # Unit tests
│   └── test_apis.py               # API client tests
│
├── 📂 notebooks/                   # Jupyter notebooks
│   └── 01_phase1_testing.ipynb    # Interactive testing
│
└── 📂 logs/                        # Application logs
    └── app.log                     # Main log file
```

---

## 🚀 Project Phases

### **Phase 1: Foundation** ✅ (Complete!)

**Deliverables:**

- ✅ Complete project structure
- ✅ API client wrappers (Gemini, HuggingFace, Materials Project)
- ✅ Configuration management
- ✅ Logging system
- ✅ Testing infrastructure
- ✅ Comprehensive documentation

**What you can do now:**

```python
from src.config.settings import Settings
from src.api.gemini_client import GeminiClient

settings = Settings()
gemini = GeminiClient(settings.gemini_api_key)

response = gemini.generate_text(
    "Explain the structure of perovskite materials"
)
print(response)
```

### **Phase 2: Paper Collection** 🔄 (Coming Next)

**Goals:**

- 📥 Automated paper downloads from arXiv
- 🔍 Intelligent paper filtering and relevance scoring
- 📊 Knowledge extraction from PDFs
- 🗃️ Paper database management

**Timeline:** Day 1 (Part 2)

### **Phase 3: Hypothesis Generation** 📋 (Planned)

**Goals:**

- 🧠 Multi-step reasoning with Gemini
- 💡 Novel hypothesis generation
- ✅ Novelty checking against existing literature
- 📋 Hypothesis ranking and validation

**Timeline:** Day 2 (Part 1)

### **Phase 4: Autonomous Agent** 🤖 (Planned)

**Goals:**

- 🔄 Fully autonomous research loop
- 🎯 Multi-agent collaboration
- 📈 Results visualization dashboard
- 📝 Automated report generation

**Timeline:** Day 2 (Part 2)

---

## 💻 Usage Examples

### **Basic: Test Individual APIs**

```python
from src.config.settings import Settings
from src.api.gemini_client import GeminiClient
from src.api.materials_project_client import MaterialsProjectClient

# Initialize
settings = Settings()

# Use Gemini for text generation
gemini = GeminiClient(settings.gemini_api_key)
explanation = gemini.generate_text(
    "What are topological insulators?",
    max_tokens=300,
    temperature=0.3
)
print(explanation)

# Search materials database
mp = MaterialsProjectClient(settings.mp_api_key)
materials = mp.search_by_formula("Fe2O3")
for mat in materials:
    print(f"{mat['formula_pretty']}: {mat['band_gap']} eV")
```

### **Intermediate: Chain Multiple APIs**

```python
# Ask Gemini for material suggestion
question = "Suggest a material for solar cell applications"
suggestion = gemini.generate_text(question, max_tokens=100)

# Extract formula (e.g., "CdTe")
formula = suggestion.split()[0]  # Simplified extraction

# Look up properties in Materials Project
properties = mp.search_by_formula(formula)
print(f"Found {len(properties)} materials matching {formula}")
```

### **Advanced: Coming in Phase 2+**

Full autonomous research pipeline with paper analysis, hypothesis generation, and validation!

---

## 🛠️ Development

### **Running Tests**

```powershell
# Test all APIs
python scripts/test_all_apis.py

# Run unit tests (requires pytest)
pip install pytest
pytest tests/ -v

# Test specific module
pytest tests/test_apis.py::TestGeminiClient -v
```

### **Logging**

Logs are automatically written to `logs/app.log`:

```python
from src.utils.logger import setup_logger

logger = setup_logger(log_level="DEBUG")
logger.info("Application started")
logger.error("Something went wrong", exc_info=True)
```

### **Configuration**

All settings in `.env`:

```bash
# API Keys
GEMINI_API_KEY=your_key
HF_TOKEN=your_token
MP_API_KEY=your_key

# Application Settings
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
CACHE_ENABLED=true          # Cache API responses
MAX_RETRIES=3               # Retry failed requests
REQUEST_TIMEOUT=30          # Timeout in seconds
```

---

## 🎓 Why This Project Matters

### **Democratizing Research**

Traditional AI research requires:

- 💰 Expensive GPUs ($1000s)
- 💾 Large model downloads (100+ GB)
- ⚡ High power consumption
- 🎓 Advanced technical skills

**This project needs:**

- 💰 $0 (free APIs)
- 💾 ~50 MB total
- ⚡ Runs on any laptop
- 🎓 Basic Python knowledge

### **Real Scientific Impact**

By combining:

- 🤖 **Large Language Models** (understanding papers)
- 🔬 **Materials Science Databases** (real experimental data)
- 🧪 **Simulation APIs** (hypothesis validation)

We can discover **novel material combinations** that humans might miss!

---

## 📊 Technical Stack

| Component        | Technology                   | Purpose                         |
| ---------------- | ---------------------------- | ------------------------------- |
| **LLM**          | Google Gemini 2.0 Flash      | Text understanding & generation |
| **Alt LLM**      | Hugging Face (Mistral, etc.) | Specialized tasks & embeddings  |
| **Materials DB** | Materials Project API        | Real materials data             |
| **Papers**       | arXiv API                    | Scientific paper access         |
| **Chemistry**    | PubChem API                  | Compound information            |
| **Language**     | Python 3.11                  | Core implementation             |
| **Logging**      | Loguru                       | Advanced logging                |
| **Data**         | Pandas, NumPy                | Data processing                 |
| **Config**       | python-dotenv                | Environment management          |

---

## 🤝 Contributing

This is a learning project, but contributions are welcome!

**Ways to contribute:**

- 🐛 Report bugs via issues
- 💡 Suggest features
- 📖 Improve documentation
- 🔧 Submit pull requests

**Development workflow:**

```powershell
# 1. Fork the repository
# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes and test
python scripts/test_all_apis.py
pytest tests/ -v

# 4. Commit changes
git commit -m "Add amazing feature"

# 5. Push and create PR
git push origin feature/amazing-feature
```

---

## 📝 License

This project is licensed under the **MIT License** - see below:

```
MIT License

Copyright (c) 2025 Autonomous Scientist Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Google** for free Gemini API access
- **Hugging Face** for open-source models and inference API
- **Materials Project** for materials science database
- **arXiv** for open access to scientific papers
- **Python community** for amazing libraries

---

## 📞 Support & Contact

- 📖 **Documentation:** Check [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md)
- 🐛 **Issues:** Open a GitHub issue
- 💬 **Discussions:** GitHub Discussions (coming soon)

---

## 🎯 Current Status

**Phase 1: ✅ COMPLETE**

```
✅ Project structure created
✅ API clients implemented (3/3)
✅ Configuration system working
✅ Logging system active
✅ Testing infrastructure ready
✅ Documentation complete
```

**Next:** Phase 2 - Paper Collection System

---

## 🚀 Getting Started Checklist

Before diving into Phase 2:

- [ ] Python 3.11.x installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`requirements.txt`)
- [ ] API keys obtained (Gemini, HuggingFace, Materials Project)
- [ ] `.env` file configured with keys
- [ ] `test_all_apis.py` passes all tests
- [ ] Explored `notebooks/01_phase1_testing.ipynb`

**All checked?** You're ready to build an autonomous scientist! 🎉

---

_Built with ❤️ for the scientific community • December 2025_
