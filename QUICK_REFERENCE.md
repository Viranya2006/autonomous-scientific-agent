# Quick Reference - Autonomous Scientific Agent

## 🚀 Daily Workflow

### Start Working

```powershell
# Navigate to project
cd "d:\Documents\THE AUTONOMOUS SCIENTIFIC AGENT"

# Activate environment
.\venv\Scripts\Activate.ps1

# Set Python path
$env:PYTHONPATH = "src"
```

### Test APIs

```powershell
# Run full test suite
python scripts\test_all_apis.py

# Expected: Gemini ✅, Materials Project ✅
```

### Use APIs in Code

```python
from api.gemini_client import GeminiClient
from api.materials_project_client import MaterialsProjectClient
from config.settings import Settings

# Initialize
settings = Settings()
gemini = GeminiClient(settings.gemini_api_key)
mp = MaterialsProjectClient(settings.mp_api_key)

# Generate text
response = gemini.generate_text("Explain perovskites")

# Query materials
materials = mp.search_by_formula("TiO2")
properties = mp.get_material_properties(materials[0])
```

## 📦 Installed Packages

```
requests==2.31.0           # HTTP requests
python-dotenv==1.0.0       # Environment variables
arxiv==2.1.0               # arXiv API
pandas==2.1.4              # Data analysis
numpy==1.26.3              # Numerical computing
networkx==3.2.1            # Graph structures
tqdm==4.66.1               # Progress bars
pyyaml==6.0.1              # YAML parsing
loguru==0.7.2              # Advanced logging
```

## 🔑 API Keys Location

**File**: `.env` (root directory)

```env
# Google Gemini
GEMINI_API_KEY=your_key_here

# HuggingFace (optional - requires paid tier)
HF_TOKEN=your_token_here

# Materials Project
MP_API_KEY=your_key_here
```

## 📊 API Client Reference

### GeminiClient

```python
from api.gemini_client import GeminiClient

client = GeminiClient(api_key="...")

# Generate text
response = client.generate_text(
    prompt="Your question",
    max_tokens=500,         # Default: 500
    temperature=0.7,        # Default: 0.7 (0.0-1.0)
    top_p=0.95             # Default: 0.95
)
```

**Features**:

- Model: gemini-2.5-flash
- Rate limit: 0.5 req/s
- Auto-retry on failure
- Exponential backoff

### MaterialsProjectClient

```python
from api.materials_project_client import MaterialsProjectClient

client = MaterialsProjectClient(api_key="...", use_cache=True)

# Search by formula
materials = client.search_by_formula(
    formula="Si",
    max_results=10  # Default: 100
)

# Get properties
properties = client.get_material_properties(
    material_id="mp-149",
    fields=["band_gap", "density", "formation_energy"]
)

# Clear cache
client.clear_cache()
```

**Features**:

- Materials Project v3 API
- Rate limit: 5 req/s
- JSON file caching
- Auto-retry on failure

## 🐛 Troubleshooting

### Import Errors

```powershell
# Make sure Python path is set
$env:PYTHONPATH = "src"
```

### API Failures

```powershell
# Check API keys
python -c "from config.settings import Settings; Settings().validate_all()"

# View logs
cat logs\app.log
```

### Module Not Found

```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Virtual Environment Issues

```powershell
# Deactivate
deactivate

# Reactivate
.\venv\Scripts\Activate.ps1
```

## 📝 Logging

**Locations**:

- Console: Color-coded, INFO and above
- File: `logs/app.log` (rotating, 10MB max)

**Levels**:

- DEBUG: Detailed debugging information
- INFO: General information
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical failures

**Usage**:

```python
from loguru import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## 🗂️ Data Storage

```
data/
├── papers/          # Downloaded arXiv papers (PDF)
├── results/         # Research outputs (JSON, CSV)
└── cache/
    └── materials_project/  # API response cache
        └── {cache_key}.json
```

**Cache Management**:

```python
# Enable/disable in .env
CACHE_ENABLED=true

# Clear programmatically
client.clear_cache()

# Or delete manually
rm -rf data/cache/materials_project/*
```

## 🧪 Testing

### Run All Tests

```powershell
python scripts\test_all_apis.py
```

### Run Unit Tests (when available)

```powershell
pytest tests/ -v
```

### Interactive Testing

```powershell
jupyter notebook notebooks/01_phase1_testing.ipynb
```

## 📚 Documentation Files

- **README.md**: Project overview
- **API_SETUP_GUIDE.md**: Get API keys
- **HUGGINGFACE_STATUS.md**: HF API situation
- **PHASE1_COMPLETE.md**: Setup summary
- **QUICK_REFERENCE.md**: This file

## ⚙️ Configuration Options

**File**: `src/config/settings.py`

Override via `.env`:

```env
# Logging
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log

# Caching
CACHE_ENABLED=true
CACHE_DIR=data/cache

# API Behavior
MAX_RETRIES=3               # Retry failed requests
REQUEST_TIMEOUT=60          # Seconds
```

## 🎯 Common Tasks

### Generate Research Summary

```python
gemini = GeminiClient(settings.gemini_api_key)
summary = gemini.generate_text(
    "Summarize the key properties of perovskite solar cells",
    max_tokens=300
)
```

### Search Materials Database

```python
mp = MaterialsProjectClient(settings.mp_api_key)

# Find materials with high band gap
materials = mp.search_by_formula("GaN")
for mat in materials[:5]:
    props = mp.get_material_properties(mat, ["band_gap"])
    print(f"{mat}: {props.get('band_gap')} eV")
```

### Batch Processing

```python
from tqdm import tqdm

formulas = ["Si", "GaN", "TiO2", "MgO"]
results = {}

for formula in tqdm(formulas):
    materials = mp.search_by_formula(formula, max_results=5)
    results[formula] = materials
```

## 💾 Save Results

```python
from utils.helpers import save_json, load_json

# Save
data = {"results": materials, "timestamp": "2025-12-30"}
save_json(data, "data/results/experiment_001.json")

# Load
loaded = load_json("data/results/experiment_001.json")
```

## 🔄 Update Project

```powershell
# Update dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python scripts\validate_setup.py
```

## 📞 Support

- Check documentation: `README.md`, `API_SETUP_GUIDE.md`
- Review logs: `logs/app.log`
- Test APIs: `python scripts\test_all_apis.py`
- API status: `HUGGINGFACE_STATUS.md`

---

**Last Updated**: 2025-12-30  
**Phase**: 1 Complete  
**Status**: Ready for Phase 2
