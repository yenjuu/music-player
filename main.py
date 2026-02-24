import os
import discord
from discord.ext import commands
import wavelink
from dotenv import load_dotenv
import logging
from typing import cast

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入 .env 檔案中的環境變數
load_dotenv()

# --- Bot 初始化 ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)


# --- Wavelink 事件監聽 ---

@bot.event
async def on_ready():
    """當 Bot 準備就緒時，連接到 Lavalink。"""
    logger.info(f'Bot 已登入為: {bot.user}')
    
    # 從環境變數讀取 Lavalink 設定
    lavalink_uri = os.getenv("LAVALINK_URI", "http://localhost:2333")
    lavalink_password = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")
    
    node = wavelink.Node(uri=lavalink_uri, password=lavalink_password)
    
    # 使用 Pool.connect 進行連接
    try:
        await wavelink.Pool.connect(client=bot, nodes=[node])
        logger.info('✅ 成功連接到 Lavalink 節點。')
    except Exception as e:
        logger.error(f'❌ 無法連接到 Lavalink: {e}')

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    """Lavalink 節點準備就緒。"""
    logger.info(f'✅ Lavalink 節點已就緒: {payload.node.identifier} (Session ID: {payload.session_id})')

@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    """當曲目結束時，自動播放佇列中的下一首。"""
    player = payload.player
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)
        
        # 可以在此處發送訊息到文字頻道
        if hasattr(player, 'text_channel') and player.text_channel:
            await player.text_channel.send(f"🎵 自動播放下一首: **{next_track.title}**")


# --- 音樂指令 ---

@bot.command(name='play', aliases=['p'])
async def play_command(ctx: commands.Context, *, search: str):
    """播放歌曲或將其加入隊列。"""
    if not ctx.author.voice:
        return await ctx.send("❌ 請先加入一個語音頻道。" )

    player: wavelink.Player
    if not ctx.voice_client:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        player = cast(wavelink.Player, ctx.voice_client)

    # 將文字頻道綁定到播放器，以便發送訊息
    player.text_channel = ctx.channel

    # 使用 wavelink.Playable.search 進行搜尋
    try:
        tracks: wavelink.Search = await wavelink.Playable.search(search)
        if not tracks:
            return await ctx.send("❌ 找不到任何歌曲。" )
    except Exception as e:
        return await ctx.send(f"搜尋時發生錯誤: {e}")

    if isinstance(tracks, wavelink.Playlist):
        added = await player.queue.put_wait(tracks)
        await ctx.send(f"✅ 已將播放列表 **{tracks.name}** 中的 **{added}** 首歌曲加入隊列。" )
    else:
        track = tracks[0]
        await player.queue.put_wait(track)
        await ctx.send(f"✅ 已將 **{track.title}** 加入隊列。" )

    if not player.playing:
        await player.play(player.queue.get())

@bot.command(name='stop', aliases=['disconnect', 'dc'])
async def stop_command(ctx: commands.Context):
    """停止播放並中斷與語音頻道的連接。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if player:
        await player.disconnect()
        await ctx.send("⏹️ 已停止播放並離開頻道。" )

@bot.command(name='skip')
async def skip_command(ctx: commands.Context):
    """跳過目前播放的歌曲。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if player and player.playing:
        await player.stop() # on_wavelink_track_end 事件會自動處理下一首
        await ctx.send("⏭️ 已跳過目前歌曲。" )

@bot.command(name='pause')
async def pause_command(ctx: commands.Context):
    """暫停播放。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if player and player.playing:
        await player.pause(True)
        await ctx.send("⏸️ 已暫停。" )

@bot.command(name='resume')
async def resume_command(ctx: commands.Context):
    """繼續播放。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if player and player.paused:
        await player.pause(False)
        await ctx.send("▶️ 已繼續播放。" )

@bot.command(name='volume')
async def volume_command(ctx: commands.Context, value: int):
    """調整音量 (0-1000)。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if player:
        await player.set_volume(value)
        await ctx.send(f"🔊 音量已設為 {value}%")

@bot.command(name='queue', aliases=['q'])
async def queue_command(ctx: commands.Context):
    """顯示目前的播放隊列。"""
    player = cast(wavelink.Player, ctx.voice_client)
    if not player or player.queue.is_empty:
        return await ctx.send("播放隊列目前是空的。" )

    queue_text = ""
    for i, track in enumerate(player.queue, start=1):
        queue_text += f"{i}. {track.title}\n"
        if i >= 10: # 最多顯示 10 首
            queue_text += f"...還有 {len(player.queue) - 10} 首"
            break
    
    embed = discord.Embed(title="播放隊列", description=queue_text, color=0x2b2d31)
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['h'])
async def help_command(ctx: commands.Context):
    """顯示機器人的指令說明。"""
    embed = discord.Embed(
        title="🎵 音樂機器人指令清單",
        description="使用 `!` 作為指令前綴。以下是目前可用的指令：",
        color=0x5865f2
    )

    embed.add_field(
        name="🚀 播放與搜尋",
        value=(
            "`!play <搜尋內容/網址>` (縮寫: `!p`)\n"
            "   └ 播放/搜尋 YouTube 歌曲或貼上連結。\n"
            "`!stop` (縮寫: `!dc`, `!disconnect`)\n"
            "   └ 停止播放清空隊列並離開頻道。"
        ),
        inline=False
    )

    embed.add_field(
        name="⏯️ 播放控制",
        value=(
            "`!pause`  - 暫停播放\n"
            "`!resume` - 繼續播放\n"
            "`!skip`   - 跳過目前歌曲\n"
            "`!volume <0-1000>` - 調整音量"
        ),
        inline=False
    )

    embed.add_field(
        name="📋 隊列管理",
        value=(
            "`!queue` (縮寫: `!q`)\n"
            "   └ 查看目前的播放隊列。"
        ),
        inline=False
    )    
    await ctx.send(embed=embed)


# --- 執行 Bot ---
def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("錯誤：DISCORD_TOKEN 環境變數未設定。" )
        return
    
    bot.run(token)

if __name__ == "__main__":
    main()