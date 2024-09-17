import typing
import logging

import instructor

from pathlib import Path
from textwrap import dedent

from tqdm import tqdm
from faster_whisper import WhisperModel, transcribe
from openai import OpenAI
from pydantic import BaseModel

from yt_extractor.youtube import interfaces as youtube_interfaces
from yt_extractor.transcription import interfaces


logger = logging.getLogger(__file__)


class Sentence(BaseModel):
    text: str
    start: float
    end: float


class WhisperPrompt(BaseModel):
    fictitious_prompt: str


class Transcriber:
    def __init__(self, whisper_model: WhisperModel, llm_client: OpenAI, llm_model: str):
        self.model = whisper_model
        self.instructor_client = instructor.from_openai(
            llm_client,
            mode=instructor.Mode.JSON,
        )
        self.llm_model = llm_model

    def _get_initial_prompt(self, video_info: youtube_interfaces.YtVideoInfo) -> str:
        # Inspired by https://cookbook.openai.com/examples/whisper_prompting_guide#fictitious-prompts-can-be-generated-by-gpt
        resp = self.instructor_client.chat.completions.create(
            model=self.llm_model,
            response_model=WhisperPrompt,
            messages=[
                {
                    "role": "system",
                    "content": dedent("""
                        You are a transcript generator.
                        Your task is to create the first few sentences of the fictional transcript of a YouTube video.
                        You will be given the TITLE and the DESCRIPTION of the video.
                        The generated content should be very relevant to the TITLE and the DESCRIPTION.
                        If the TITLE and the DESCRIPTION implies the video is a conversation,
                        never diarize speakers or add quotation marks;
                        instead, write all transcripts in a normal paragraph of text without speakers identified.
                        Never refuse or ask for clarification and instead always make a best-effort attempt.
                        Have a proper punctuation (.?!) when a sentences ends.
                    """),
                },
                {
                    "role": "user",
                    "content": dedent(f"""
                        TITLE:
                        {video_info.title}

                        DESCRIPTION:
                        {video_info.processed_info.cleaned_description}
                    """),
                },
            ],
        )
        return f"{video_info.title}. {video_info.processed_info.cleaned_description} {resp.fictitious_prompt}"

    def transcribe_full_text(
        self, audio_path: Path, video_info: youtube_interfaces.YtVideoInfo
    ) -> str:
        initial_prompt = self._get_initial_prompt(video_info=video_info)
        logger.info(f"Initial prompt: {initial_prompt}")
        segments, transcribe_info = self.model.transcribe(
            audio=audio_path,
            initial_prompt=initial_prompt,
        )
        transcribed = ""
        audio_duration = round(transcribe_info.duration, 2)
        current_timestamp = 0.0
        with tqdm(
            total=audio_duration,
            unit=" audio seconds",
            desc="Faster Whisper transcription",
        ) as progress_bar:
            for segment in segments:
                transcribed += segment.text
                progress_bar.update(segment.end - current_timestamp)
                current_timestamp = segment.end
            if current_timestamp < audio_duration:  # silence at the end of the audio
                progress_bar.update(audio_duration - current_timestamp)

        return transcribed

    def transcribe_by_chapter(
        self, audio_path: Path, video_info: youtube_interfaces.YtVideoInfo
    ) -> typing.Sequence[interfaces.ChapterTranscription]:
        initial_prompt = self._get_initial_prompt(video_info=video_info)
        logger.info(f"Initial prompt: {initial_prompt}")
        segments, transcribe_info = self.model.transcribe(
            audio=audio_path,
            initial_prompt=initial_prompt,
            word_timestamps=True,
        )

        audio_duration = round(transcribe_info.duration, 2)
        current_timestamp = 0.0

        sentences: typing.List[Sentence] = []
        current_sentence_words: typing.List[transcribe.Word] = []

        with tqdm(
            total=audio_duration,
            unit=" audio seconds",
            desc="Faster Whisper transcription",
        ) as progress_bar:
            for segment in segments:
                for word in segment.words:
                    current_sentence_words.append(word)
                    if word.word.endswith((".", "?", "!")):
                        sentences.append(
                            Sentence(
                                start=current_sentence_words[0].start,
                                end=current_sentence_words[-1].end,
                                text="".join(
                                    word.word for word in current_sentence_words
                                ),
                            )
                        )
                        current_sentence_words = []
                progress_bar.update(segment.end - current_timestamp)
                current_timestamp = segment.end
            if len(current_sentence_words) != 0:
                sentences.append(
                    Sentence(
                        start=current_sentence_words[0].start,
                        end=current_sentence_words[-1].end,
                        text="".join(word.word for word in current_sentence_words),
                    )
                )
            if current_timestamp < audio_duration:  # silence at the end of the audio
                progress_bar.update(audio_duration - current_timestamp)

        if len(video_info.chapters) == 0:
            return [
                interfaces.ChapterTranscription(
                    title="Untitled Chapter", text="".join(s.text for s in sentences)
                )
            ]

        chapters_iterator = iter(video_info.chapters)
        current_chapter = next(chapters_iterator)
        chapter_transcriptions: typing.List[interfaces.ChapterTranscription] = []
        current_chapter_transcription = interfaces.ChapterTranscription(
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
                    current_chapter_transcription = interfaces.ChapterTranscription(
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
        sentence_length = max(0.01, sentence_end - sentence_start)
        latest_start = max(sentence_start, chapter_start)
        earliest_end = min(sentence_end, chapter_end)
        delta = max(0, earliest_end - latest_start)
        return delta / sentence_length
