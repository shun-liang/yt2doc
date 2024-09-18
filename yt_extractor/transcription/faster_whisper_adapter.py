import typing

from pathlib import Path

from faster_whisper import WhisperModel

from yt_extractor.transcription import interfaces


class FasterWhisperAdapter:
    def __init__(self, whisper_model: WhisperModel) -> None:
        self.whisper_model = whisper_model

    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[interfaces.WhisperSegment]:
        segments, _ = self.whisper_model.transcribe(
            audio=audio_path, initial_prompt=initial_prompt
        )
        return (
            interfaces.WhisperSegment(
                start=segment.start, end=segment.end, text=segment.text
            )
            for segment in segments
        )
