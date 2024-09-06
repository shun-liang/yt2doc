import typing
import logging

from pathlib import Path
from dataclasses import dataclass

from faster_whisper import WhisperModel


logger = logging.getLogger(__name__)


class Chapter(typing.Protocol):
    title: str
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
            while segment.start > current_chapter.end_time:
                current_chapter = next(chapters_iterator)
                chapter_transcriptions.append(current_chapter_transcription)
                current_chapter_transcription = ChapterTranscription(
                    title=current_chapter.title, text=""
                )
            current_chapter_transcription.text += segment.text
        chapter_transcriptions.append(current_chapter_transcription)

        return chapter_transcriptions
