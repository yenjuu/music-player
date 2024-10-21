import os
import discord
from discord.ext import commands
from playerCmd import PlayerCmd
from keepAlive import keep_alive

# Description: 主執行類，繼承自 discord.ext.commands.Bot
class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())
        self.music_players = {}

    def get_player(self, guild_id):
        return self.music_players.get(guild_id)       


bot = MusicBot()

@bot.event
async def on_ready():
    print(f'Bot已登入為 {bot.user}')
    await bot.add_cog(PlayerCmd(bot))

# 啟動 KeepAlive 服務
keep_alive()

# 在這裡替換成你的機器人 Token
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)