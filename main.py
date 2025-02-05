import os
import discord
from discord.ext import commands
from playerCmd import PlayerCmd
from keepAlive import keep_alive
from dotenv import load_dotenv
import subprocess
import logging
import base64

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 檢查 FFmpeg 是否安裝
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        logger.info("FFmpeg 已正確安裝")
        return True
    except FileNotFoundError:
        logger.error("FFmpeg 未安裝！")
        return False

# 確保加載 .env 文件
load_dotenv()

# Description: 主執行類，繼承自 discord.ext.commands.Bot
class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.music_players = {}

    def get_player(self, guild_id):
        return self.music_players.get(guild_id)       

    async def setup_hook(self):
        await self.add_cog(PlayerCmd(self))

    async def on_ready(self):
        # 設置機器人的狀態
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="!p 點歌"
        )
        await self.change_presence(activity=activity)
        print(f'Bot已登入為 {self.user}')

bot = MusicBot()

if __name__ == "__main__":
    # 處理 cookies
    cookies = os.getenv('COOKIES')
    if cookies:
        try:
            cookies_data = base64.b64decode(cookies).decode('utf-8')
            with open('cookies.txt', 'w', encoding='utf-8', newline='\n') as f:
                f.write(cookies_data)
            logger.info("成功載入 cookies")
        except Exception as e:
            logger.error(f"載入 cookies 時發生錯誤: {str(e)}")

    # 啟動 web server 來保持活躍
    keep_alive()
    
    if not check_ffmpeg():
        logger.error("請先安裝 FFmpeg！")
        exit(1)
    
    TOKEN = os.getenv("TOKEN")
    if TOKEN is None:
        raise ValueError("No TOKEN found in environment variables. Please check your .env file.")

    bot.run(TOKEN)