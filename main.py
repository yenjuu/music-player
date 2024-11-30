import os
import discord
from discord.ext import commands
from playerCmd import PlayerCmd
from keepAlive import keep_alive
from dotenv import load_dotenv

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

# 啟動 KeepAlive 服務
keep_alive()

# 在這裡替換成你的機器人 Token
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("No TOKEN found in environment variables. Please check your .env file.")

bot.run(TOKEN)