@echo off
echo ========================================
echo CSIS Backend Server
echo ========================================
echo.

cd backend

echo [1/2] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo.
echo [2/2] Starting FastAPI server...
echo.
echo Server will start at: http://localhost:8000
echo WebSocket endpoint: ws://localhost:8000/ws
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
