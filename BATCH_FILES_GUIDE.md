# 🚀 Quick Start - Batch File Launchers

## One-Click Launchers for Easy Access

I've created convenient batch files for easy one-click launching of the Autonomous Scientific Agent!

---

## 📋 Available Batch Files

### 1. **launcher.bat** ⭐ RECOMMENDED
**The main launcher with an interactive menu**

Double-click to see options:
1. **Start Dashboard** - Opens the interactive GUI
2. **Run Research** - Executes the research agent
3. **Start Dashboard + Run Research** - Both at once
4. **Open Documentation** - View guides
5. **Exit**

**Best for**: General use, beginners, accessing all features

---

### 2. **start_dashboard.bat**
**Quick launcher for the dashboard only**

- Opens Streamlit dashboard at `http://localhost:8501`
- Interactive GUI for session management
- View results and create new research sessions

**Best for**: When you only need the GUI

---

### 3. **run_research.bat**
**Quick launcher for research execution**

- Runs the autonomous research agent
- Execute research from command line
- Requires session_id configuration

**Best for**: Running research after creating a session

---

### 4. **install.bat**
**One-time package installation**

- Installs all required Python packages
- Uses `requirements.txt`
- Run once before first use

**Best for**: Initial setup, package updates

---

## 🎯 Usage Guide

### First Time Setup

1. **Install packages** (one time only):
   ```
   Double-click: install.bat
   ```

2. **Configure API keys**:
   - Edit `.env` file with your API keys:
     ```
     GEMINI_API_KEY=your_key_here
     GROQ_API_KEY=your_key_here
     MP_API_KEY=your_key_here
     ```

3. **Launch application**:
   ```
   Double-click: launcher.bat
   ```

### Daily Usage

**Option A: Interactive Menu (Recommended)**
```
Double-click: launcher.bat
Select option from menu
```

**Option B: Dashboard Only**
```
Double-click: start_dashboard.bat
Opens GUI at http://localhost:8501
```

**Option C: Research Only**
```
1. Create session in dashboard
2. Edit scripts/run_agent.py with session_id
3. Double-click: run_research.bat
```

---

## 📊 Workflow Example

### Complete Research Workflow

1. **Start the dashboard**:
   - Double-click `launcher.bat`
   - Select option 1 (Start Dashboard)
   - Browser opens to `http://localhost:8501`

2. **Create a research session**:
   - Go to "🏠 Home" tab
   - Fill out research form
   - Click "🚀 Start Research"
   - Copy the `session_id`

3. **Configure the agent**:
   - Edit `scripts/run_agent.py`
   - Set `session_id = "session_20241231_143022"`

4. **Run research**:
   - Double-click `run_research.bat` OR
   - Use `launcher.bat` → option 2

5. **Watch live progress**:
   - Dashboard shows real-time updates
   - 0% → 100% progress bar
   - Current phase tracking

6. **View results**:
   - Check all tabs in dashboard
   - Review papers, hypotheses, experiments
   - See discoveries!

---

## 🔧 Troubleshooting

### Dashboard won't start
- Check if Streamlit is installed: Run `install.bat`
- Verify Python is in PATH
- Try manual start: `streamlit run dashboard/app.py`

### Research agent fails
- Verify API keys in `.env` file
- Check session_id in `scripts/run_agent.py`
- Run `install.bat` to update packages

### Port already in use
- Another Streamlit instance is running
- Close other Streamlit windows
- Or use: `streamlit run dashboard/app.py --server.port 8502`

### Python not found
- Install Python 3.11 or higher
- Add Python to system PATH
- Restart terminal/command prompt

---

## 💡 Tips & Tricks

### Tip 1: Keep Dashboard Open
Always keep the dashboard running while research executes to see live progress updates.

### Tip 2: Multiple Sessions
You can create multiple research sessions and switch between them in the dashboard.

### Tip 3: Background Research
Start dashboard with `launcher.bat` option 1, then run research in a separate window with option 2.

### Tip 4: Quick Access
Create desktop shortcuts to `launcher.bat` for fastest access.

### Tip 5: Session Management
Use the Home tab to view, manage, and delete old research sessions.

---

## 📁 File Locations

```
THE AUTONOMOUS SCIENTIFIC AGENT/
├── launcher.bat              ⭐ Main launcher (menu)
├── start_dashboard.bat       🎨 Dashboard only
├── run_research.bat          🔬 Research only
├── install.bat               📦 Package installer
├── .env                      🔑 API keys (configure this!)
├── dashboard/
│   └── app.py               🖥️  Streamlit dashboard
├── scripts/
│   └── run_agent.py         🤖 Research agent
└── data/
    ├── sessions.db          💾 Session database
    └── agent_results/       📊 Research results
```

---

## 🎨 Customization

### Change Default Settings

Edit `scripts/run_agent.py` to change defaults:
```python
query = "your default research topic"
max_papers = 20
max_hypotheses = 10
max_iterations = 3
```

### Add Custom Launcher

Create your own `.bat` file:
```batch
@echo off
cd /d "%~dp0"
streamlit run dashboard/app.py --server.port 8502
pause
```

---

## 🚀 Quick Reference

| Task | Batch File | Time |
|------|-----------|------|
| First time setup | `install.bat` | ~2 min |
| Start everything | `launcher.bat` → 1 | <10 sec |
| Dashboard only | `start_dashboard.bat` | <5 sec |
| Run research | `run_research.bat` | Varies |
| Full workflow | `launcher.bat` → 3 | Varies |

---

## 🎉 Benefits

✅ **No command line needed** - Just double-click!  
✅ **Interactive menu** - Choose what to run  
✅ **Automatic navigation** - Finds correct directories  
✅ **Error messages** - Clear feedback  
✅ **Documentation access** - Built-in help  
✅ **Beginner friendly** - Easy for anyone  

---

## 📞 Need Help?

- 📖 Read: `INTERACTIVE_GUIDE.md` - Complete user manual
- 📝 Check: `IMPROVEMENTS_COMPLETE.md` - Features overview
- 🔍 View: `README.md` - Project documentation
- 💬 Issues: Check error messages in console

---

## 🌟 Pro Mode

Want more control? You can still use command line:

```bash
# Start dashboard
streamlit run dashboard/app.py

# Run research
cd scripts
python run_agent.py

# Run tests
python -m pytest tests/

# Check sessions
python -c "from src.utils.session_manager import SessionManager; print(SessionManager().list_sessions())"
```

---

**Happy Researching! Just double-click and go! 🚀🧬✨**
