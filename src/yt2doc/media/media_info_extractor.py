import typing
import logging

import yt_dlp

from pathlib import Path

from pydantic import BaseModel, Field

from yt2doc.media import interfaces


logger = logging.getLogger(__file__)


class YtDLPResponse(BaseModel):
    video_id: str = Field(alias="id")
    webpage_url: str
    webpage_url_domain: str
    title: str
    description: str
    chapters: typing.Optional[typing.Sequence[interfaces.MediaChapter]] = None


class YtDLPPlaylistEntry(BaseModel):
    url: str
    title: str


class YtDLPPlaylistResponse(BaseModel):
    title: str
    entries: typing.Sequence[YtDLPPlaylistEntry]


def _length(chapter: interfaces.MediaChapter) -> float:
    return chapter.end_time - chapter.start_time


def _merge_short_chapters(
    chapters: typing.Sequence[interfaces.MediaChapter],
) -> typing.Sequence[interfaces.MediaChapter]:
    threshold_seconds = 60
    merged_chapters: typing.List[interfaces.MediaChapter] = []
    for idx, chapter in enumerate(chapters):
        if idx == 0:
            merged_chapters.append(chapter)
            continue

        merged_target: interfaces.MediaChapter
        merged_target = merged_chapters[-1]
        if (
            _length(chapter) < threshold_seconds
            and _length(merged_target) < threshold_seconds
        ):
            merged_chapter = interfaces.MediaChapter(
                title=merged_target.title + " & " + chapter.title,
                start_time=merged_target.start_time,
                end_time=chapter.end_time,
            )
            merged_chapters = merged_chapters[:-1] + [merged_chapter]
        else:
            merged_chapters.append(chapter)

    return merged_chapters


class MediaInfoExtractor:
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir

    def extract_media_info(self, video_url: str) -> interfaces.MediaInfo:
        ydl_opts = {
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            response = ydl.extract_info(video_url, download=False)

        parsed_response = YtDLPResponse(**response)

        return interfaces.MediaInfo(
            video_id=parsed_response.video_id,
            title=parsed_response.title,
            webpage_url=parsed_response.webpage_url,
            webpage_url_domain=parsed_response.webpage_url_domain,
            chapters=_merge_short_chapters(parsed_response.chapters or []),
            description=parsed_response.description,
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

        parsed_response = YtDLPResponse(**response)
        audio_path = self.temp_dir / f"{parsed_response.video_id}.m4a"
        return audio_path

    def extract_playlist_info(self, playlist_url: str) -> interfaces.YtPlaylistInfo:
        ydl_opts = {
            "extract_flat": "in_playlist",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)

        parsed_playlist_info = YtDLPPlaylistResponse(**playlist_info)

        video_urls = [
            entry.url
            for entry in parsed_playlist_info.entries
            if entry.title not in ["[Private video]", "[Deleted video]"]
        ]
        return interfaces.YtPlaylistInfo(
            title=parsed_playlist_info.title,
            video_urls=video_urls,
        )
