import os
import asyncio
from yt_dlp import YoutubeDL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import sys
import io
import logging

# 設置日誌記錄
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/bot.log', encoding='utf-8'),
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
            'force-ipv4': True,
            'prefer-insecure': True,
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
            
            async def extract_info():
                with YoutubeDL(ydl_opts) as ydl:
                    try:
                        logger.info(f"正在處理URL: {self.url}")
                        info = ydl.extract_info(self.url, download=False)
                        return info
                    except Exception as e:
                        logger.error(f"YDL錯誤: {str(e)}")
                        raise

            info = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: asyncio.run(extract_info())
            )
            
            if not info:
                raise Exception("無法獲取影片資訊")

            if 'entries' in info:
                info = info['entries'][0]

            self.title = info.get('title', 'Unknown title')
            logger.info(f"成功獲取影片資訊: {self.title}")
            
            self.url = info.get('url')
            if not self.url:
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
            
            logger.info(f"處理完成。URL: {self.url[:50]}...")
            return self

        except Exception as e:
            logger.error(f"發生錯誤: {str(e)}")
            raise Exception(f"處理影片時發生錯誤: {str(e)}")