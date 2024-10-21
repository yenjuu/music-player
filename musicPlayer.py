import discord
import asyncio
from async_timeout import timeout
import datetime

# Description: 音樂播放器，用於管理和控制Discord伺服器中的音樂播放。
class MusicPlayer:
    def __init__(self, ctx):
        # 初始化音樂播放器
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog

        self.queue = asyncio.Queue()  # 創建一個異步隊列來存儲音樂
        self.next = asyncio.Event()  # 用於控制下一首歌曲的播放

        self.volume = 0.3  # 設置默認音量
        self.current = None  # 當前播放的歌曲
        self.playing = False  # 是否正在播放
        self.paused = False  # 是否暫停

        ctx.bot.loop.create_task(self.player_loop())  # 啟動播放循環

    async def player_loop(self):
        # 音樂播放的主循環
        await self.bot.wait_until_ready()  # 等待機器人準備就緒

        while not self.bot.is_closed():
            self.next.clear()  # 清除下一首歌曲的事件標記

            try:
                async with timeout(300):  # 5分鐘沒活動就退出
                    self.current = await self.queue.get()  # 從隊列中獲取下一首歌曲
            except asyncio.TimeoutError:
                return self.destroy(self.guild)  # 超時後清理資源

            try:
                # 增加更多的 FFmpeg 選項
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn -filter:a volume=1.0'
                }
                
                # 創建音頻源時添加錯誤處理
                try:
                    audio_source = discord.FFmpegPCMAudio(
                        self.current.url,
                        **ffmpeg_options
                    )
                    self.current.source = discord.PCMVolumeTransformer(
                        audio_source,
                        volume=self.volume
                    )
                except Exception as e:
                    await self.channel.send(f'創建音頻源時發生錯誤: {str(e)}')
                    continue

                self.playing = True
                self.guild.voice_client.play(
                    self.current.source,
                    after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set)
                )

                # 發送當前播放信息
                await self.channel.send(
                    f'🎵 現在播放: {self.current.title}\n'
                    f'長度: {datetime.timedelta(seconds=self.current.duration)}\n'
                    f'音量: {self.volume * 100}%'
                )

            except Exception as e:
                await self.channel.send(f'播放時發生錯誤: {str(e)}')
            finally:
                await self.next.wait()  # 等待當前歌曲播放完成
                self.current = None
                self.playing = False

    def destroy(self, guild):
        # 清理資源並停止播放
        return self.bot.loop.create_task(self.cog.cleanup(guild))