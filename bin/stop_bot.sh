#!/bin/bash

# 切換到腳本所在目錄的上層
cd "$(dirname "$0")"
cd ..

echo "Stopping Discord bot..."
if pkill -f "python main.py"; then
    echo "Bot stopped successfully."
else
    echo "No running bot found."
fi

read -p "Press Enter to continue..." 