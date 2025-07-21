@echo off
setlocal enabledelayedexpansion
title Report Generator V1.0.0

echo.
echo ========================================
echo   Report Generator V1.0.0
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if main.py exists
if not exist "src\main.py" (
    echo Error: Cannot find src\main.py
    echo Please make sure you are running this file in the correct directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo This program requires Python 3.8 or higher to run.
    echo Please install Python from: https://www.python.org/downloads/
    echo.
    echo Installation tips:
    echo 1. Download Python 3.8 or newer
    echo 2. During installation, check "Add Python to PATH"
    echo 3. Restart your computer after installation
    echo 4. Try running this script again
    echo.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check pip installation
echo Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: pip is not available
    echo pip should come with Python installation
    echo Please reinstall Python with pip included
    echo.
    pause
    exit /b 1
)

REM Check dependencies
echo Checking dependencies...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing required dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo.
        echo Possible solutions:
        echo 1. Check your internet connection
        echo 2. Try running as administrator
        echo 3. Update pip: python -m pip install --upgrade pip
        echo 4. Install manually: pip install pandas openpyxl matplotlib tkinter
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
)

echo.
echo Starting Report Generator...
echo.

REM Start the main program
python src\main.py

REM Check if program ran successfully
if errorlevel 1 (
    echo.
    echo ERROR: Program encountered an error
    echo.
    echo Please check the log files for detailed error information:
    echo Log location: logs\app_%date:~0,4%%date:~5,2%%date:~8,2%.log
    echo.
    echo Common solutions:
    echo 1. Make sure all required files are present
    echo 2. Check if data files are in correct format
    echo 3. Verify Python and dependencies are properly installed
    echo.
) else (
    echo.
    echo Program completed successfully!
)

echo.
echo Press any key to close this window...
pause >nul