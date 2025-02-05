#!/bin/bash
# 設定環境變數
export DEBIAN_FRONTEND=noninteractive

# 更新套件列表
apt-get update

# 安裝 FFmpeg
apt-get install -y ffmpeg

# 安裝 Python 依賴
pip install -r requirements.txt 