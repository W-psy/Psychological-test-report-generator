@echo off
chcp 65001 >nul
title 版本管理工具

echo.
echo ==========================================
echo           版本管理工具
echo ==========================================
echo.

:menu
echo 请选择操作：
echo.
echo 1. 查看当前版本状态
echo 2. 更新版本号
echo 3. 创建Git标签
echo 4. 构建可执行文件
echo 5. 完整发布流程
echo 6. 退出
echo.
set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto status
if "%choice%"=="2" goto update
if "%choice%"=="3" goto tag
if "%choice%"=="4" goto build
if "%choice%"=="5" goto release
if "%choice%"=="6" goto exit
echo 无效选项，请重新选择
goto menu

:status
echo.
echo 📋 当前版本状态：
python scripts\version_manager.py status
echo.
pause
goto menu

:update
echo.
set /p version=请输入新版本号 (例如: 1.1.0): 
set /p desc=请输入版本描述 (可选): 
echo.
python scripts\version_manager.py update %version% "%desc%"
echo.
pause
goto menu

:tag
echo.
set /p version=请输入版本号: 
set /p message=请输入标签消息 (可选): 
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
set /p version=请输入发布版本号: 
set /p desc=请输入发布描述: 
echo.
echo ⚠️  警告：这将执行完整的发布流程
echo    - 更新版本号
echo    - 创建Git提交和标签
echo    - 构建可执行文件
echo.
set /p confirm=确认继续？(y/N): 
if /i not "%confirm%"=="y" goto menu

python scripts\version_manager.py release %version% "%desc%"
echo.
pause
goto menu

:exit
echo.
echo 👋 再见！
timeout /t 2 >nul
exit

:error
echo.
echo ❌ 发生错误，请检查：
echo    1. 是否安装了Python
echo    2. 是否在正确的项目目录中
echo    3. 是否安装了Git
echo.
pause
goto menu