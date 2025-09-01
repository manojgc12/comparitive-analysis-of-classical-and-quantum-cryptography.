@echo off
REM Quantum-Safe Cryptography Suite - GUI Launcher for Windows
REM Double-click this file to launch the GUI application

title Quantum-Safe Cryptography Suite - GUI Launcher

echo.
echo ================================================
echo  Quantum-Safe Cryptography Suite - GUI Launcher
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

echo Python found. Starting GUI application...
echo.

REM Launch the GUI using the launcher script
python run_gui.py

REM If the launcher fails, try direct execution
if %errorlevel% neq 0 (
    echo.
    echo Launcher script failed. Trying direct execution...
    python gui_application.py
)

REM Keep window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo  Application failed to start
    echo ========================================
    echo.
    echo Troubleshooting steps:
    echo 1. Ensure Python 3.8+ is installed
    echo 2. Install required packages: pip install -r requirements.txt
    echo 3. Check that all project files are present
    echo 4. Try running: python run_gui.py
    echo.
    pause
)
