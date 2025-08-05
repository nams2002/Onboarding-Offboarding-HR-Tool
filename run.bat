@echo off
echo 🚀 Starting Rapid Innovation Onboarding Automation System...
echo ============================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create images directory if it doesn't exist
if not exist "images" (
    mkdir images
    echo 📁 Created images directory
)

echo ============================================================
echo 🌐 Launching Streamlit application...
echo 📱 The application will open in your default web browser
echo 🔗 URL: http://localhost:8501
echo ============================================================
echo Press Ctrl+C to stop the application
echo ============================================================

REM Launch Streamlit
streamlit run app.py

pause
