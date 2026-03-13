@echo off
echo ========================================
echo CSIS Backend - Installing Dependencies
echo ========================================
echo.

cd backend

echo [1/3] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Python packages...
echo This may take 5-10 minutes...
echo.

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed!
    pause
    exit /b 1
)

echo.
echo [3/3] Downloading YOLOv8 model...
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

echo.
echo ========================================
echo ✅ Installation Complete!
echo ========================================
echo.
echo To start the backend server, run:
echo   start_backend.bat
echo.
pause
