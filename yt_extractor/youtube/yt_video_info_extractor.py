import logging

import yt_dlp

from pathlib import Path

from yt_extractor.youtube import interfaces


logger = logging.getLogger(__file__)


class YtVideoInfoExtractor:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def extract_video_info(self, video_url: str) -> interfaces.YtVideoInfo:
        ydl_opts = {
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            response = ydl.extract_info(video_url, download=False)

        video_id = response["id"]
        title = response["title"]
        chapter_objects = response["chapters"] if response["chapters"] else []
        chapters = [interfaces.YtChapter(**chapter) for chapter in chapter_objects]
        description = response["description"]

        return interfaces.YtVideoInfo(
            video_id=video_id,
            title=title,
            chapters=chapters,
            description=description,
        )

    def extract_audio(self, video_url: str) -> Path:
        ydl_opts = {
            "quiet": True,
            "noprogress": True,
            "outtmpl": f"{self.temp_dir}/%(id)s.%(ext)s",
            "format": "m4a/bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            response = ydl.extract_info(video_url, download=True)

        video_id = response["id"]
        audio_path = self.temp_dir / f"{video_id}.m4a"
        return audio_path

    def extract_playlist_info(self, playlist_url: str) -> interfaces.YtPlaylistInfo:
        ydl_opts = {
            "extract_flat": "in_playlist",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)

        title: str = playlist_info["title"]
        entries = playlist_info["entries"]
        video_urls = [
            entry["url"]
            for entry in entries
            if entry["title"] not in ["[Private video]", "[Deleted video]"]
        ]
        return interfaces.YtPlaylistInfo(
            title=title,
            video_urls=video_urls,
        )
