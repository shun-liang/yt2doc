import typing

from pathlib import Path

from pydantic import BaseModel


class YtChapter(BaseModel):
    title: str
    start_time: float
    end_time: float


class YtVideoInfo(BaseModel):
    video_id: str
    title: str
    chapters: typing.Sequence[YtChapter]
    description: str


class YtPlaylistInfo(BaseModel):
    title: str
    video_urls: typing.Sequence[str]


class IYtVideoInfoExtractor(typing.Protocol):
    def extract_video_info(self, video_url: str) -> YtVideoInfo: ...
    def extract_audio(self, video_url: str) -> Path: ...
    def extract_playlist_info(self, playlist_url: str) -> YtPlaylistInfo: ...
