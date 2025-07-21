@echo off
cd /d "%~dp0"
echo Starting Report Generator...
python src\main.py
if errorlevel 1 (
    echo Program encountered an error
    pause
    exit /b 1
)
echo Program finished. Press any key to close...
pause >nul