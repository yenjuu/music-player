# 使用官方 Python 映像作為基礎
FROM python:3.10-slim

# 安裝 FFmpeg 和其他必要的包
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 設置工作目錄
WORKDIR /app

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程序代碼
COPY . .

# 啟動命令
CMD ["python", "main.py"] 