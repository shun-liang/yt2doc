import typing
import logging

import yt_dlp

from pathlib import Path

from yt2doc.youtube import interfaces


logger = logging.getLogger(__file__)


def _length(chapter: interfaces.YtChapter) -> float:
    return chapter.end_time - chapter.start_time


def _merge_short_chapters(
    chapters: typing.Sequence[interfaces.YtChapter],
) -> typing.Sequence[interfaces.YtChapter]:
    threshold_seconds = 60
    merged_chapters: typing.List[interfaces.YtChapter] = []
    for idx, chapter in enumerate(chapters):
        if idx == 0:
            merged_chapters.append(chapter)
            continue

        merged_target: interfaces.YtChapter
        merged_target = merged_chapters[-1]
        if (
            _length(chapter) < threshold_seconds
            and _length(merged_target) < threshold_seconds
        ):
            merged_chapter = interfaces.YtChapter(
                title=merged_target.title + " & " + chapter.title,
                start_time=merged_target.start_time,
                end_time=chapter.end_time,
            )
            merged_chapters = merged_chapters[:-1] + [merged_chapter]
        else:
            merged_chapters.append(chapter)

    return merged_chapters


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
        chapter_objects = response.get("chapters") or []
        chapters = _merge_short_chapters(
            [interfaces.YtChapter(**chapter) for chapter in chapter_objects]
        )
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
