import typing

from pathlib import Path

from faster_whisper import WhisperModel

from yt2doc.transcription import interfaces


class FasterWhisperAdapter:
    def __init__(self, whisper_model: WhisperModel) -> None:
        self.whisper_model = whisper_model

    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[interfaces.Segment]:
        segments, _ = self.whisper_model.transcribe(
            audio=audio_path, initial_prompt=initial_prompt
        )
        return (
            interfaces.Segment(start=segment.start, end=segment.end, text=segment.text)
            for segment in segments
        )
