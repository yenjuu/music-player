@echo off
chcp 65001 > nul
cd /d "%~dp0"
cd ..

:: 查找並終止 Python 程序
echo Stopping Discord bot...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main*nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Bot stopped successfully.
) else (
    echo No running bot found.
)

pause 