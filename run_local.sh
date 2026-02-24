#!/bin/bash

# 當腳本結束時自動關閉背景程序
trap "kill 0" EXIT

# 確保 log 資料夾存在
mkdir -p log

echo "🚀 Starting Lavalink..."
cd lavalink
java -jar Lavalink.jar > ../log/lavalink.log 2>&1 &
LAVALINK_PID=$!
cd ..

echo "⏳ Waiting 5 seconds for Lavalink to initialize..."
sleep 5

# 檢查是否啟動成功
if ! ps -p $LAVALINK_PID > /dev/null; then
    echo "❌ Failed to start Lavalink. Please check lavalink.log for errors."
    exit 1
fi

echo "🤖 Starting Discord Bot..."

# 檢查虛擬環境
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

python main.py
