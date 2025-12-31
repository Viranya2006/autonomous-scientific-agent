@echo off
REM Complete Launcher for Autonomous Scientific Agent
REM Provides menu to start dashboard or run research

:MENU
cls
echo ========================================
echo  AUTONOMOUS SCIENTIFIC AGENT
echo  One-Click Launcher
echo ========================================
echo.
echo Select an option:
echo.
echo 1. Start Dashboard (Interactive GUI)
echo 2. Run Research (Execute Agent)
echo 3. Start Dashboard + Run Research
echo 4. Open Documentation
echo 5. Exit
echo.
echo ========================================
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto DASHBOARD
if "%choice%"=="2" goto RESEARCH
if "%choice%"=="3" goto BOTH
if "%choice%"=="4" goto DOCS
if "%choice%"=="5" goto EXIT

echo Invalid choice. Please try again.
timeout /t 2 > nul
goto MENU

:DASHBOARD
cls
echo Starting Dashboard...
echo.
cd /d "%~dp0"
start cmd /k "streamlit run dashboard/app.py"
echo.
echo Dashboard starting in new window...
echo Open browser to: http://localhost:8501
echo.
timeout /t 3
goto MENU

:RESEARCH
cls
echo Starting Research Agent...
echo.
echo IMPORTANT: Create a session in the dashboard first!
echo Then edit scripts/run_agent.py with your session_id
echo.
pause
echo.
cd /d "%~dp0"
cd scripts
python run_agent.py
echo.
pause
goto MENU

:BOTH
cls
echo Starting Dashboard and Research...
echo.
cd /d "%~dp0"
start cmd /k "streamlit run dashboard/app.py"
echo Dashboard started in new window...
echo.
echo Waiting 5 seconds for dashboard to load...
timeout /t 5 > nul
echo.
echo Now starting research agent...
cd scripts
python run_agent.py
echo.
pause
goto MENU

:DOCS
cls
echo Opening Documentation...
echo.
cd /d "%~dp0"
if exist "INTERACTIVE_GUIDE.md" (
    start INTERACTIVE_GUIDE.md
) else (
    echo INTERACTIVE_GUIDE.md not found!
)
if exist "README.md" (
    start README.md
)
timeout /t 2
goto MENU

:EXIT
cls
echo.
echo Thanks for using Autonomous Scientific Agent!
echo.
timeout /t 2 > nul
exit
