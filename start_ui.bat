@echo off
REM Start Streamlit UI for AI Response Caching System

echo Starting Streamlit UI...
echo.
echo Make sure FastAPI backend is running on http://127.0.0.1:8000
echo.

cd /d "%~dp0"
streamlit run ui/app.py

pause
