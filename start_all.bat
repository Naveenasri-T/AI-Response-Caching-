`@echo off
REM Start both FastAPI backend and Streamlit UI

echo ========================================
echo AI Response Caching System
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    if exist "fastapienv\Scripts\activate.bat" (
        echo Activating virtual environment...
        call fastapienv\Scripts\activate.bat
    ) else (
        echo Warning: Virtual environment not found
        echo Please activate it manually or install dependencies
        echo.
    )
)

echo Starting services...
echo.

REM Start FastAPI in a new window
echo [1/2] Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait a bit for FastAPI to start
timeout /t 5 /nobreak > nul

REM Start Streamlit in a new window
echo [2/2] Starting Streamlit UI...
start "Streamlit UI" cmd /k "streamlit run ui/app.py"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo FastAPI Backend: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo Streamlit UI: http://localhost:8501
echo.
echo Press any key to stop all services...
pause > nul

REM Kill the processes when user presses a key
taskkill /FI "WINDOWTITLE eq FastAPI Backend*" /F > nul 2>&1
taskkill /FI "WINDOWTITLE eq Streamlit UI*" /F > nul 2>&1

echo.
echo All services stopped.
pause
