import typing

from pathlib import Path

from pydantic import BaseModel

from yt2doc.media import interfaces as youtube_interfaces


class Segment(BaseModel):
    start: float
    end: float
    text: str


class ChapterTranscription(BaseModel):
    title: str
    segments: typing.Sequence[Segment]


class Transcription(BaseModel):
    language: str
    chapters: typing.Sequence[ChapterTranscription]


class IWhisperAdapter(typing.Protocol):
    def detect_language(self, audio_path: Path) -> str: ...

    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[Segment]: ...


class ITranscriber(typing.Protocol):
    def transcribe(
        self, audio_path: Path, video_info: youtube_interfaces.MediaInfo
    ) -> Transcription: ...
