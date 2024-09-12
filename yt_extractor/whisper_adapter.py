import typing
import logging

from pathlib import Path
from dataclasses import dataclass

from faster_whisper import WhisperModel, transcribe


logger = logging.getLogger(__file__)


@dataclass
class Sentence:
    text: str
    start: float
    end: float


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

    def transcribe_by_chapter(
        self, audio_path: Path, title: str, chapters: typing.Sequence[Chapter]
    ) -> typing.Sequence[ChapterTranscription]:
        segments, _ = self.model.transcribe(
            audio=audio_path,
            initial_prompt=title,
            word_timestamps=True,
        )

        sentences: typing.List[Sentence] = []
        current_sentence_words: typing.List[transcribe.Word] = []

        for segment in segments:
            for word in segment.words:
                current_sentence_words.append(word)
                if word.word.endswith((".", "?", "!")):
                    sentences.append(
                        Sentence(
                            start=current_sentence_words[0].start,
                            end=current_sentence_words[-1].end,
                            text="".join(word.word for word in current_sentence_words),
                        )
                    )
                    current_sentence_words = []
        if len(current_sentence_words) != 0:
            sentences.append(
                Sentence(
                    start=current_sentence_words[0].start,
                    end=current_sentence_words[-1].end,
                    text="".join(word.word for word in current_sentence_words),
                )
            )

        if len(chapters) == 0:
            return [
                ChapterTranscription(
                    title="Untitled Chapter", text="".join(s.text for s in sentences)
                )
            ]

        chapters_iterator = iter(chapters)
        current_chapter = next(chapters_iterator)
        chapter_transcriptions: typing.List[ChapterTranscription] = []
        current_chapter_transcription = ChapterTranscription(
            title=current_chapter.title, text=""
        )
        for sentence in sentences:
            while (
                self._calculate_overlap(
                    sentence_start=sentence.start,
                    sentence_end=sentence.end,
                    chapter_start=current_chapter.start_time,
                    chapter_end=current_chapter.end_time,
                )
                < 0.5
            ):
                try:
                    current_chapter = next(chapters_iterator)
                except StopIteration:
                    break
                else:
                    chapter_transcriptions.append(current_chapter_transcription)
                    current_chapter_transcription = ChapterTranscription(
                        title=current_chapter.title, text=""
                    )

            current_chapter_transcription.text += sentence.text

        chapter_transcriptions.append(current_chapter_transcription)

        return chapter_transcriptions

    @staticmethod
    # Inspired by https://stackoverflow.com/a/9044111
    def _calculate_overlap(
        sentence_start: float,
        sentence_end: float,
        chapter_start: float,
        chapter_end: float,
    ) -> float:
        sentence_length = sentence_end - sentence_start
        latest_start = max(sentence_start, chapter_start)
        earliest_end = min(sentence_end, chapter_end)
        delta = max(0, earliest_end - latest_start)
        return delta / sentence_length
