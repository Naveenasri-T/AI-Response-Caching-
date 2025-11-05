@echo off
echo ========================================
echo AI Response Caching POC - Quick Start
echo ========================================
echo.

echo [1/3] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [2/3] Checking .env file...
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

echo [3/3] Starting services with Docker Compose...
echo.
docker-compose up --build

echo.
echo ========================================
echo Services stopped. Goodbye!
echo ========================================
pause
