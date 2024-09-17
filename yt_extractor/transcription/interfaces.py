import typing

from pathlib import Path

from pydantic import BaseModel

from yt_extractor.youtube import interfaces as youtube_interfaces


class ChapterTranscription(BaseModel):
    title: str
    text: str


class ITranscriber(typing.Protocol):
    def transcribe_full_text(
        self,
        audio_path: Path,
        video_info: youtube_interfaces.YtVideoInfo,
    ) -> str: ...

    def transcribe_by_chapter(
        self, audio_path: Path, video_info: youtube_interfaces.YtVideoInfo
    ) -> typing.Sequence[ChapterTranscription]: ...
