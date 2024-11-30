@echo off
cd /d "%~dp0"
cd ..

:: 顯示當前目錄（偵錯用）
echo Current directory: %CD%

:: 創建 log 目錄（如果不存在）
if not exist "log" mkdir log

:: 檢查虛擬環境
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

:: 檢查 Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python not found!
    pause
    exit /b 1
)

:: 檢查 main.py
if not exist "main.py" (
    echo Error: main.py not found!
    pause
    exit /b 1
)

:: 啟動機器人並將輸出重定向到日誌文件
echo Starting bot...
start /min cmd /c "venv\Scripts\activate.bat && python main.py > log\bot.log 2>&1"

:: 等待確認啟動
timeout /t 2 /nobreak > nul
echo Bot started in background.
echo Check log\bot.log for any error messages.

pause

exit 