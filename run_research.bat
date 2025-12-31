@echo off
REM Run Autonomous Scientific Agent
REM One-click launcher for research execution

echo ========================================
echo  Autonomous Scientific Agent
echo ========================================
echo.
echo Starting autonomous research...
echo.
echo To use session tracking:
echo 1. Create a session in the dashboard first
echo 2. Edit scripts/run_agent.py with your session_id
echo.
echo Press any key to start research...
pause > nul
echo.

cd /d "%~dp0"
cd scripts
python run_agent.py

echo.
echo ========================================
echo Research complete! Check the dashboard for results.
echo Run: start_dashboard.bat
echo ========================================
echo.
pause
