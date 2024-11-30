#!/bin/bash

# 切換到腳本所在目錄的上層
cd "$(dirname "$0")"
cd ..

# 顯示當前目錄（偵錯用）
echo "Current directory: $(pwd)"

# 創建 log 目錄（如果不存在）
mkdir -p log

# 檢查虛擬環境
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    read -p "Press Enter to continue..."
    exit 1
fi

# 檢查 Python
if ! command -v python &> /dev/null; then
    echo "Error: Python not found!"
    read -p "Press Enter to continue..."
    exit 1
fi

# 檢查 main.py
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found!"
    read -p "Press Enter to continue..."
    exit 1
fi

# 啟動機器人並將輸出重定向到日誌文件
echo "Starting bot..."
source venv/bin/activate
nohup python main.py > log/bot.log 2>&1 &

# 等待確認啟動
sleep 2
echo "Bot started in background."
echo "Check log/bot.log for any error messages."

# 等待用戶按下 Enter
read -p "Press Enter to continue..."
 