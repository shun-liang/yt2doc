import typing

from pathlib import Path

from pydantic import BaseModel

from yt_extractor.youtube import interfaces as youtube_interfaces


class ChapterTranscription(BaseModel):
    title: str
    text: str


class WhisperSegment(BaseModel):
    start: float
    end: float
    text: str


class IWhisperAdapter(typing.Protocol):
    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[WhisperSegment]: ...


class ITranscriber(typing.Protocol):
    def transcribe_by_chapter(
        self, audio_path: Path, video_info: youtube_interfaces.YtVideoInfo
    ) -> typing.Sequence[ChapterTranscription]: ...
