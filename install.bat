@echo off
REM Install required Python packages
REM Run this once before first use

echo ========================================
echo  Autonomous Scientific Agent
echo  Package Installation
echo ========================================
echo.
echo This will install all required Python packages.
echo.
echo Required packages:
echo - streamlit
echo - pandas
echo - plotly
echo - scikit-learn
echo - google-generativeai
echo - groq
echo - mp-api
echo - arxiv
echo - python-dotenv
echo - loguru
echo.
echo Press any key to start installation...
pause > nul
echo.

cd /d "%~dp0"

echo Installing packages...
echo.
pip install -r requirements.txt

echo.
echo ========================================
echo Installation complete!
echo.
echo Next steps:
echo 1. Configure your API keys in .env file
echo 2. Run launcher.bat to start the application
echo ========================================
echo.
pause
