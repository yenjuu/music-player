# 🎵 Professional Discord Music Bot

一個基於 `discord.py` 和 `Wavelink` (Lavalink) 構建的高品質音樂機器人。

## 🚀 快速開始

### 環境要求
- **Python**: 3.12+ 
- **Java**: JDK 21+ (執行 Lavalink 伺服器所需)
- **Lavalink**: 專案已附帶 `Lavalink.jar`

### 本地安裝步驟

1. **複製專案並安裝依賴**:
   ```bash
   # 創建虛擬環境
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   
   # 安裝依賴
   pip install -r requirements.txt
   ```

2. **設定環境變數**:
   在根目錄創建 `.env` 檔案，內容如下：
   ```env
   DISCORD_TOKEN=你的_DISCORD_BOT_TOKEN
   LAVALINK_URI=http://localhost:2333
   LAVALINK_PASSWORD=youshallnotpass
   PORT=8080
   ```

3. **啟動 Lavalink 伺服器**:
   ```bash
   cd lavalink
   java -jar Lavalink.jar
   ```

4. **啟動機器人**:
   ```bash
   python main.py
   ```

## ☁️ 部署說明

### 部署到 Render / Zeabur
專案已包含 `Dockerfile` 和 `render.yaml`，可快速部署：
1. 將專案推送到 GitHub。
2. 在部署平台連結 GitHub 儲存庫。
3. **重要設定**：
   - 確保環境變數 `DISCORD_TOKEN` 已正確填寫。
   - 伺服器會自動執行 `build.sh` 來啟動 Lavalink 和 Bot。

## 🛠️ 指令清單
- `!play <搜尋/連結>` - 播放音樂。
- `!skip` - 跳過目前歌曲。
- `!pause` / `!resume` - 暫停與繼續。
- `!queue` - 查看待播放清單。
- `!help` - 查看詳細指令說明。

## 📄 專案結構
- `main.py`: 機器人主要邏輯。
- `lavalink/`: 包含 Lavalink 核心組件與配置。
- `cookies.txt`: YouTube 搜尋優化設定。
- `keepAlive.py`: 保持機器人活躍的 Flask 伺服器。
