# Interactive Dashboard Guide

## 🎉 New Interactive Features

The Autonomous Scientific Agent now includes a fully interactive dashboard with session management, live progress tracking, and error recovery!

## 🚀 Getting Started

### 1. Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`

### 2. Navigate to Home Tab

The **Home** tab is your research control center with two main sections:

#### 🆕 Launch New Research

Fill out the research form:
- **Research Topic**: Enter your scientific question (e.g., "high-entropy alloys for hydrogen storage")
- **Max Papers**: Number of papers to collect (5-100)
- **Max Hypotheses**: Number of hypotheses to generate (3-50)
- **Iterations**: Research cycles to run (1-10)
- **AI Model**: Choose between `gemini` or `groq`

Click **🚀 Start Research** to create a new research session.

#### 📋 Active Sessions

View all your research sessions with:
- **Status indicators**: ⏳ Pending | 🔄 Running | ✅ Completed | ❌ Failed
- **Live progress bars**: See real-time progress (0-100%)
- **Current phase**: Know what the agent is doing
- **Session management**: Delete old sessions

## 📊 Session Tracking

### Understanding Session Status

| Status | Emoji | Meaning |
|--------|-------|---------|
| Pending | ⏳ | Session created, waiting to run |
| Running | 🔄 | Agent actively researching |
| Completed | ✅ | Research finished successfully |
| Failed | ❌ | Error occurred during research |

### Progress Phases

The agent reports progress through these phases:

1. **Starting** (0%) - Initializing research
2. **Collecting Papers** (10%) - Searching arXiv
3. **Papers Collected** (20%) - Papers downloaded
4. **Analyzing Papers** (30%) - AI analyzing content
5. **Analysis Complete** (45%) - Gaps identified
6. **Generating Hypotheses** (55%) - Creating testable ideas
7. **Hypotheses Generated** (65%) - Hypotheses ready
8. **Testing Hypotheses** (75%) - Computational validation
9. **Testing Complete** (85%) - Tests finished
10. **Evaluating Results** (90%) - Finding discoveries
11. **Discoveries Found** (95%) - Promising results identified
12. **Completed** (100%) - Research done!

## 🔄 Running Research with Sessions

### Method 1: Manual Execution

After creating a session in the dashboard:

1. Copy the `session_id` (e.g., `session_20241231_143022`)
2. Edit `scripts/run_agent.py`:
   ```python
   session_id = "session_20241231_143022"  # Your session ID
   ```
3. Run the agent:
   ```bash
   cd scripts
   python run_agent.py
   ```

The dashboard will show live progress updates!

### Method 2: Command Line with Session

You can also run with session tracking directly:

```python
from src.agent.autonomous_agent import AutonomousScientist
from src.utils.session_manager import SessionManager

# Create session
session_mgr = SessionManager()
session_id = session_mgr.create_session(
    research_topic="your topic here",
    max_papers=20,
    max_hypotheses=10,
    iterations=3
)

# Run research
agent = AutonomousScientist()
summary = agent.run(
    query="your topic here",
    max_papers=20,
    session_id=session_id  # Track progress!
)
agent.save_results(session_id=session_id)
```

## 🛠️ Error Recovery Features

### Failed Paper Analyses

The **Papers** tab now shows failed analyses separately:

- **⚠️ Failed Analyses** expandable section at top
- Shows papers that failed due to API errors/timeouts
- Each failed paper has a **🔄 Retry** button
- Error messages explain what went wrong

### Automatic Retry Logic

The system now automatically retries failed operations:
- **3 attempts** with exponential backoff (2s, 4s, 8s)
- Applies to: entity extraction, classification, deep analysis
- Logs each retry attempt for debugging

### Failed Analysis Data

Failed papers are saved with:
- `key_findings: ["Analysis failed"]`
- `research_significance: "Analysis failed: [error message]"`
- `relevance_score: 0.0`
- Full error details in logs

## 📈 Viewing Results

### Overview Tab
- **Metrics**: Total papers, hypotheses, tests, discoveries
- **Charts**: Novelty distribution, feasibility analysis
- **Test results**: Pass/fail distribution

### Papers Tab
- **Failed analyses section**: Review and retry failed papers
- **Search and filter**: Find specific papers
- **Sort options**: By relevance, title, or date
- **Full details**: Abstract, findings, arXiv link

### Hypotheses Tab
- **Filter by novelty**: Minimum novelty score slider
- **Filter by feasibility**: High/Medium/Low categories
- **Search**: Find specific hypotheses
- **Detailed view**: Materials, methods, expected outcomes

### Experiments Tab
- **Filter by result**: Show PASS/FAIL/INCONCLUSIVE
- **Color-coded**: 🟢 Pass | 🔴 Fail | 🟡 Inconclusive
- **Evidence**: Computational validation data
- **Confidence**: Test confidence scores

### Discoveries Tab
- **Promising results**: High-confidence findings
- **Iteration tracking**: Which cycle found it
- **Evidence**: Supporting data
- **Confidence scores**: Validation strength

## 🎯 Best Practices

### 1. Create Sessions First
Always create a session in the dashboard before running research to get live progress tracking.

### 2. Monitor Progress
Keep the dashboard open while research runs to see real-time updates and catch errors early.

### 3. Review Failed Papers
Check the Failed Analyses section after each run. Many failures are due to temporary API issues and can be retried.

### 4. Start Small
For new topics, start with:
- Max Papers: 10-20
- Max Hypotheses: 5-10
- Iterations: 1-2

### 5. Session Management
Delete old/failed sessions regularly to keep the dashboard clean:
- Click **🗑️ Delete** on any session
- Failed sessions remain visible until deleted

## 🔍 Troubleshooting

### Dashboard Not Updating?
Click **🔄 Refresh Data** in the sidebar.

### Session Stuck at 0%?
The agent might not be running. Check:
1. Is `run_agent.py` executing?
2. Is the session_id correct?
3. Check logs for errors

### Many Failed Papers?
Common causes:
- **API quota exceeded**: Wait and retry later
- **Network issues**: Check internet connection
- **Invalid API keys**: Verify `.env` file

### No Progress Updates?
Ensure you're passing `session_id` to `agent.run()`:
```python
agent.run(query="...", session_id=session_id)
```

## 📚 Database Location

Sessions are stored in SQLite database:
- **Location**: `data/sessions.db`
- **Tables**: `sessions` and `session_logs`
- **Backup**: Copy this file to save session history

## 🎓 Advanced Usage

### Query Session Details

```python
from src.utils.session_manager import SessionManager

session_mgr = SessionManager()

# List all sessions
sessions = session_mgr.list_sessions()

# Get specific session
session = session_mgr.get_session("session_20241231_143022")

# Get session logs
logs = session_mgr.get_session_logs("session_20241231_143022")
```

### Manual Progress Updates

```python
session_mgr.update_session_progress(
    session_id="session_20241231_143022",
    progress=50,
    phase="Custom Phase",
    message="Custom status message"
)
```

### Mark Session Complete

```python
session_mgr.update_session_status(
    session_id="session_20241231_143022",
    status="completed"
)
```

## 🌟 Next Steps

1. **Create your first session** in the Home tab
2. **Run the agent** with session tracking
3. **Watch live progress** in the dashboard
4. **Review results** across all tabs
5. **Retry failed papers** as needed
6. **Iterate and improve** your research!

---

**Happy Researching! 🧬🔬✨**
