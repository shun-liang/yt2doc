import typing
import logging

from pathlib import Path
from dataclasses import dataclass

from faster_whisper import WhisperModel


logger = logging.getLogger(__name__)


class Chapter(typing.Protocol):
    title: str
    start_time: float
    end_time: float


@dataclass
class ChapterTranscription:
    title: str
    text: str


class WhisperAdapter:
    def __init__(self, model: WhisperModel):
        self.model = model

    def transcribe_full_text(self, audio_path: Path) -> str:
        segments, _ = self.model.transcribe(audio=audio_path)
        return "".join(s.text for s in segments)

    def transcribe_by_chapter(self, audio_path: Path, chapters: typing.List[Chapter]):
        segments, _ = self.model.transcribe(audio=audio_path)

        if len(chapters) == 0:
            return [
                ChapterTranscription(title="", text="".join(s.text for s in segments))
            ]

        chapters_iterator = iter(chapters)
        current_chapter = next(chapters_iterator)
        chapter_transcriptions: typing.List[ChapterTranscription] = []
        current_chapter_transcription = ChapterTranscription(
            title=current_chapter.title, text=""
        )
        for segment in segments:
            while (
                self._calculate_overlap(
                    segment_start=segment.start,
                    segment_end=segment.end,
                    chapter_start=current_chapter.start_time,
                    chapter_end=current_chapter.end_time,
                )
                < 0.5
            ):
                current_chapter = next(chapters_iterator)
                chapter_transcriptions.append(current_chapter_transcription)
                current_chapter_transcription = ChapterTranscription(
                    title=current_chapter.title, text=""
                )
            current_chapter_transcription.text += segment.text
        chapter_transcriptions.append(current_chapter_transcription)

        return chapter_transcriptions

    @staticmethod
    # Inspired by https://stackoverflow.com/a/9044111
    def _calculate_overlap(
        segment_start: float,
        segment_end: float,
        chapter_start: float,
        chapter_end: float,
    ) -> float:
        segment_length = segment_end - segment_start
        latest_start = max(segment_start, chapter_start)
        earlist_end = min(segment_end, chapter_end)
        delta = max(0, earlist_end - latest_start)
        return delta / segment_length
