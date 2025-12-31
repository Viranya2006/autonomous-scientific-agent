@echo off
REM Start Autonomous Scientific Agent Dashboard
REM One-click launcher for the interactive dashboard

echo ========================================
echo  Autonomous Scientific Agent Dashboard
echo ========================================
echo.
echo Starting Streamlit dashboard...
echo.
echo The dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo ========================================
echo.

cd /d "%~dp0"
streamlit run dashboard/app.py

pause
