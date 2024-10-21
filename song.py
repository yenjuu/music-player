import os
import asyncio
from yt_dlp import YoutubeDL

# Description: 用於處理音樂資訊和下載
class Song:
    def __init__(self, url_or_search, requester):
        self.requester = requester
        self.url = url_or_search
        self.title = None
        self.duration = None
        self.thumbnail = None

    async def create(self):
        # 從環境變數中取得 Cookie 內容
        cookies_content = os.environ.get("YT_COOKIES")

        # 如果環境變數存在，寫入 cookies.txt
        if cookies_content:
            with open('cookies.txt', 'w') as f:
                f.write(cookies_content)

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'cookiefile': 'cookies.txt'
        }
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                try:
                    print(f"正在處理URL: {self.url}")  # 偵錯用
                    info = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: ydl.extract_info(self.url, download=False)
                    )
                    
                    if not info:
                        raise Exception("無法獲取影片資訊")

                    # 如果是播放清單搜索結果，獲取第一個條目
                    if 'entries' in info:
                        info = info['entries'][0]

                    print(f"成功獲取影片資訊: {info.get('title')}")  # 偵錯用
                    
                    self.title = info.get('title', 'Unknown title')
                    self.url = info.get('url')  # 對於 yt-dlp，直接使用 'url' 字段
                    if not self.url:
                        # 備用方案：如果找不到直接的 URL，使用最佳音頻格式
                        formats = info.get('formats', [])
                        audio_formats = [
                            f for f in formats 
                            if f.get('acodec') != 'none' and f.get('vcodec') == 'none'
                        ]
                        if audio_formats:
                            best_audio = max(
                                audio_formats,
                                key=lambda f: f.get('abr', 0) if f.get('abr') else 0
                            )
                            self.url = best_audio['url']
                        else:
                            self.url = formats[0]['url']
                    
                    self.duration = info.get('duration', 0)
                    self.thumbnail = info.get('thumbnail')
                    print(f"處理完成。URL: {self.url[:50]}...")  # 偵錯用
                    return self

                except Exception as e:
                    print(f"發生錯誤: {str(e)}")  # 偵錯用
                    raise Exception(f"無法處理URL: {str(e)}")

        except Exception as e:
            raise Exception(f"處理影片時發生錯誤: {str(e)}")