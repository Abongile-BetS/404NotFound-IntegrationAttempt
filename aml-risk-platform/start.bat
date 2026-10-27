@echo off
title AML Risk Intelligence Platform
cd /d "%~dp0"

echo ============================================
echo   AML Risk Intelligence Platform
echo ============================================
echo.
echo Preparing the application. This may take a few minutes the first time...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-local.ps1"
if errorlevel 1 (
    echo.
    echo Setup failed. Please check the messages above.
    pause
    exit /b 1
)

echo.
echo Loading demo data (first run may take a minute)...
echo.

"%~dp0backend\.venv\Scripts\python.exe" "%~dp0backend\seed.py"
if errorlevel 1 (
    echo.
    echo Demo data loading failed. Continuing anyway...
)

echo.
echo Starting the application...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-local.ps1"
if errorlevel 1 (
    echo.
    echo Startup failed. Please check the messages above.
    pause
    exit /b 1
)

echo.
echo Waiting for the app to become ready...
timeout /t 8 /nobreak >nul

start http://localhost:5173

echo.
echo The app should now be open in your browser.
echo If not, visit: http://localhost:5173
echo.
pause