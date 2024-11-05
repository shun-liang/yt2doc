import typing

from pathlib import Path

from pydantic import BaseModel


class MediaChapter(BaseModel):
    title: str
    start_time: float
    end_time: float


class MediaInfo(BaseModel):
    video_id: str
    title: str
    webpage_url: str
    webpage_url_domain: str
    chapters: typing.Sequence[MediaChapter]
    description: str


class YtPlaylistInfo(BaseModel):
    title: str
    video_urls: typing.Sequence[str]


class IYtMediaInfoExtractor(typing.Protocol):
    def extract_media_info(self, video_url: str) -> MediaInfo: ...
    def extract_audio(self, video_url: str) -> Path: ...
    def extract_playlist_info(self, playlist_url: str) -> YtPlaylistInfo: ...
