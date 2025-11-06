@echo off
REM This script runs image processing using your system Python (not venv)
REM to avoid the PyTorch DLL issue in the virtual environment

echo Testing with system Python...
python --version
python tests\test_local_image.py

pause
