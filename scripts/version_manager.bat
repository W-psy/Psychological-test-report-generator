@echo off
chcp 65001 >nul
title Version Manager

echo.
echo ==========================================
echo           Version Management Tool
echo ==========================================
echo.

:menu
echo Please select an option:
echo.
echo 1. View current version status
echo 2. Update version number
echo 3. Create Git tag
echo 4. Build executable
echo 5. Complete release process
echo 6. Exit
echo.
set /p choice=Enter option (1-6): 

if "%choice%"=="1" goto status
if "%choice%"=="2" goto update
if "%choice%"=="3" goto tag
if "%choice%"=="4" goto build
if "%choice%"=="5" goto release
if "%choice%"=="6" goto exit
echo Invalid option, please try again
goto menu

:status
echo.
echo Current version status:
python scripts\version_manager.py status
echo.
pause
goto menu

:update
echo.
set /p version=Enter new version number (e.g. 1.1.0): 
set /p desc=Enter version description (optional): 
echo.
python scripts\version_manager.py update %version% "%desc%"
echo.
pause
goto menu

:tag
echo.
set /p version=Enter version number: 
set /p message=Enter tag message (optional): 
echo.
python scripts\version_manager.py tag %version% "%message%"
echo.
pause
goto menu

:build
echo.
python scripts\version_manager.py build
echo.
pause
goto menu

:release
echo.
set /p version=Enter release version number: 
set /p desc=Enter release description: 
echo.
echo WARNING: This will execute the complete release process
echo    - Update version number
echo    - Create Git commit and tag
echo    - Build executable
echo.
set /p confirm=Confirm to continue? (y/N): 
if /i not "%confirm%"=="y" goto menu

python scripts\version_manager.py release %version% "%desc%"
echo.
pause
goto menu

:exit
echo.
echo Goodbye!
timeout /t 2 >nul
exit

:error
echo.
echo Error occurred, please check:
echo    1. Is Python installed?
echo    2. Are you in the correct project directory?
echo    3. Is Git installed?
echo.
pause
goto menu