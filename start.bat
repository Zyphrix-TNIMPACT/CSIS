@echo off
echo ========================================
echo CSIS - Cognitive Safety Intelligence System
echo Installation Script
echo ========================================
echo.

echo [1/3] Installing dependencies...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed!
    echo Please make sure Node.js is installed.
    pause
    exit /b 1
)

echo.
echo [2/3] Installation complete!
echo.
echo [3/3] Starting CSIS application...
echo.
echo The application will open in your browser at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm start
