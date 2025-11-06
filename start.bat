@echo off
echo ========================================
echo AI Response Caching POC - Quick Start
echo ========================================
echo.

echo [1/4] Checking system Python transformers...
python -c "from transformers import pipeline; print('OK')" >nul 2>&1
if errorlevel 1 (
    echo   Installing transformers in system Python...
    python -m pip install transformers pillow torch torchvision --quiet
    echo   ✓ Installation complete
) else (
    echo   ✓ Transformers already installed
)

echo [2/4] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo   ✓ Docker is running

echo [3/4] Checking .env file...
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env file with your API keys.
    echo.
    echo Required variables:
    echo   GROQ_API_KEY=your_key_here
    echo   HF_API_KEY=your_key_here
    echo.
    pause
)
echo   ✓ .env file exists

echo [4/4] Starting FastAPI server...
echo.
echo   Server will be available at: http://localhost:8000
echo   API docs at: http://localhost:8000/docs
echo.
echo   Press CTRL+C to stop
echo.

call fastapienv\Scripts\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ========================================
echo Server stopped. Goodbye!
echo ========================================
pause
