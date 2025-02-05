import os
import asyncio
from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import sys
import io
import logging

# 設置日誌記錄（只使用 StreamHandler）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Description: 用於處理音樂資訊和下載
class Song:
    def __init__(self, url_or_search, requester):
        self.requester = requester
        self.url = url_or_search
        self.title = None
        self.duration = None
        self.thumbnail = None
        
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        ))

    def is_spotify_url(self, url):
        return 'spotify.com' in url
    
    async def get_spotify_track_info(self, url):
        track_id = url.split('/')[-1].split('?')[0]
        track = self.sp.track(track_id)
        search_query = f"{track['artists'][0]['name']} - {track['name']}"
        return search_query

    async def _get_best_audio_url(self, formats):
        """Extract best audio URL from formats."""
        audio_formats = [
            f for f in formats 
            if f.get('acodec') != 'none' and f.get('vcodec') == 'none'
        ]
        if not audio_formats:
            return formats[0]['url']
        best_audio = max(
            audio_formats,
            key=lambda f: f.get('abr', 0) if f.get('abr') else 0
        )
        return best_audio['url']

    async def _extract_with_retry(self, ydl, retries=3):
        """Extract info with retry mechanism."""
        for attempt in range(retries):
            try:
                return ydl.extract_info(self.url, download=False)
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"嘗試 {attempt + 1}/{retries} 失敗: {str(e)}")
                    await asyncio.sleep(1)
                    continue
                raise

    async def create(self):
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
            'cookiefile': 'cookies.txt',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['webpage', 'configs', 'js'],
                    'max_comments': 0,
                }
            },
            'socket_timeout': 30,
            'extract_flat': True,
            'youtube_include_dash_manifest': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'encoding': 'utf-8'
        }
        
        try:
            if self.is_spotify_url(self.url):
                self.url = await self.get_spotify_track_info(self.url)
            
            info = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: asyncio.run(self._extract_with_retry(YoutubeDL(ydl_opts)))
            )
            
            if not info:
                raise Exception("無法獲取影片資訊")

            if 'entries' in info:
                info = info['entries'][0]

            self.title = info.get('title', 'Unknown title')
            logger.info(f"成功獲取影片資訊: {self.title}")
            
            self.url = info.get('url') or await self._get_best_audio_url(info.get('formats', []))
            self.duration = info.get('duration', 0)
            self.thumbnail = info.get('thumbnail')
            
            logger.info(f"處理完成。URL: {self.url[:50]}...")
            return self

        except Exception as e:
            logger.error(f"發生錯誤: {str(e)}")
            raise Exception(f"處理影片時發生錯誤: {str(e)}")