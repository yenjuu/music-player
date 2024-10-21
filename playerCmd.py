import discord
from discord.ext import commands
from async_timeout import timeout
import itertools
import datetime
from song import Song  # 引入 Song 類別
from musicPlayer import MusicPlayer  # 引入 MusicPlayer

# Description: 定義音樂播放器指令
class PlayerCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.commands_help = {
            'play': {
                'description': '播放 YouTube 影片或播放清單',
                'usage': '!play <URL或搜尋關鍵字>',
                'aliases': ['p']
            },
            'queue': {
                'description': '顯示目前的播放清單',
                'usage': '!queue',
                'aliases': ['q']
            },
            'volume': {
                'description': '調整播放音量 (0-100)',
                'usage': '!volume <數字>',
                'aliases': ['vol']
            },
            'pause': {
                'description': '暫停目前播放的歌曲',
                'usage': '!pause',
                'aliases': []
            },
            'resume': {
                'description': '繼續播放已暫停的歌曲',
                'usage': '!resume',
                'aliases': []
            },
            'skip': {
                'description': '跳過目前播放的歌曲',
                'usage': '!skip',
                'aliases': []
            },
            'stop': {
                'description': '停止播放並清空播放清單',
                'usage': '!stop',
                'aliases': []
            },
            'np': {
                'description': '顯示目前正在播放的歌曲資訊',
                'usage': '!np',
                'aliases': ['now_playing']
            }
        }

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, url):
        """播放 YouTube 影片"""
        if not ctx.author.voice:
            return await ctx.send('你需要先加入語音頻道！')

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        player = self.get_player(ctx)

        try:
            song = await Song(url, ctx.author).create()
            await player.queue.put(song)
            await ctx.send(f'👍 已加入播放清單: {song.title}')
        except Exception as e:
            await ctx.send(f'發生錯誤: {str(e)}')

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """顯示播放清單"""
        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('播放清單是空的')

        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        fmt = '\n'.join(f'**{idx+1}.** {song.title}' for idx, song in enumerate(upcoming))
        embed = discord.Embed(title=f'接下來播放 - {len(upcoming)} 首歌', description=fmt)

        if player.current:
            embed.add_field(name='現正播放', value=player.current.title, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int):
        """調整音量 (0-100)"""
        if not ctx.voice_client:
            return await ctx.send('未連接至語音頻道')

        if not 0 <= volume <= 100:
            return await ctx.send('音量必須在 0 到 100 之間')

        player = self.get_player(ctx)
        player.volume = volume / 100
        if player.current:
            player.current.source.volume = player.volume

        await ctx.send(f'🔊 音量設定為: {volume}%')

    @commands.command(name='pause')
    async def pause(self, ctx):
        """暫停播放"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send('⏸️ 已暫停播放')

    @commands.command(name='resume')
    async def resume(self, ctx):
        """繼續播放"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send('▶️ 繼續播放')

    @commands.command(name='skip')
    async def skip(self, ctx):
        """跳過目前播放的歌曲"""
        if not ctx.voice_client:
            return await ctx.send('未連接至語音頻道')

        if not ctx.voice_client.is_playing():
            return await ctx.send('目前沒有在播放任何歌曲')

        ctx.voice_client.stop()
        await ctx.send('⏭️ 跳過當前歌曲')

    @commands.command(name='stop')
    async def stop(self, ctx):
        """停止播放並清空播放清單"""
        player = self.get_player(ctx)
        player.queue._queue.clear()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('⏹️ 已停止播放並清空播放清單')

    @commands.command(name='np', aliases=['now_playing'])
    async def now_playing(self, ctx):
        """顯示目前播放資訊"""
        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('目前沒有在播放任何歌曲')

        embed = discord.Embed(title='現正播放', description=player.current.title)
        embed.add_field(name='請求者', value=player.current.requester.name)
        embed.add_field(name='時長', value=str(datetime.timedelta(seconds=player.current.duration)))
        if player.current.thumbnail:
            embed.set_thumbnail(url=player.current.thumbnail)
        
        await ctx.send(embed=embed)

    @commands.command(name='h')
    async def help(self, ctx):
        """顯示所有可用的音樂指令"""
        embed = discord.Embed(
            title="🎵 音樂機器人指令清單",
            description="以下是所有可用的指令及其說明",
            color=discord.Color.blue()
        )

        for cmd_name, cmd_info in self.commands_help.items():
            # 準備指令的完整說明
            value = f"說明：{cmd_info['description']}\n"
            value += f"用法：`{cmd_info['usage']}`\n"
            
            # 如果有別名，則添加別名信息
            if cmd_info['aliases']:
                aliases = ', '.join([f'!{alias}' for alias in cmd_info['aliases']])
                value += f"別名：`{aliases}`"

            # 添加到 embed
            embed.add_field(
                name=f"!{cmd_name}",
                value=value,
                inline=False
            )

        # 添加一些額外信息
        embed.set_footer(text="提示：在指令後面加上空格和參數來使用，例如：!play 音樂名稱")
        
        # 發送 embed 訊息
        await ctx.send(embed=embed)
