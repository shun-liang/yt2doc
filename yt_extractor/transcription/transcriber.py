import typing
import logging

import uuid
import ffmpeg
import instructor

from pathlib import Path
from textwrap import dedent

from tqdm import tqdm
from faster_whisper import WhisperModel
from openai import OpenAI
from pydantic import BaseModel

from yt_extractor.youtube import interfaces as youtube_interfaces
from yt_extractor.transcription import interfaces


logger = logging.getLogger(__file__)


class Segment(BaseModel):
    start: float
    end: float
    text: str


class Sentence(BaseModel):
    text: str
    start: float
    end: float


class WhisperPrompt(BaseModel):
    fictitious_prompt: str


class Transcriber:
    def __init__(
        self,
        temp_dir: Path,
        whisper_model: WhisperModel,
        llm_client: OpenAI,
        llm_model: str,
    ):
        self.temp_dir = temp_dir
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

    def _get_audio_chunk_for_chapter(
        self, audio_path: Path, chapter: youtube_interfaces.YtChapter
    ) -> Path:
        duration = chapter.end_time - chapter.start_time
        ext = audio_path.suffix
        file_path = self.temp_dir / f"{uuid.uuid4().hex}{ext}"
        ffmpeg.input(
            filename=audio_path.as_posix(), ss=chapter.start_time, t=duration
        ).output(file_path.as_posix()).run()
        return file_path

    def transcribe_full_text(
        self, audio_path: Path, video_info: youtube_interfaces.YtVideoInfo
    ) -> str:
        initial_prompt = self._get_initial_prompt(video_info=video_info)
        logger.info(f"Initial prompt: {initial_prompt}")
        segments, transcribe_info = self.model.transcribe(
            audio=audio_path,
            initial_prompt=initial_prompt,
            vad_filter=True,
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
        chaptered_transcriptions: typing.List[interfaces.ChapterTranscription] = []
        full_audio_duration: float = float(
            ffmpeg.probe(audio_path)["format"]["duration"]
        )
        rounded_full_audio_duration = round(full_audio_duration, 2)
        current_timestamp = 0.0
        with tqdm(
            total=rounded_full_audio_duration,
            unit=" audio seconds",
            desc="Faster Whisper transcription",
        ) as progress_bar:
            for chapter in video_info.chapters:
                audio_chunk_path = self._get_audio_chunk_for_chapter(
                    audio_path=audio_path, chapter=chapter
                )

                chapter_segments: typing.List[Segment] = []

                segments, _ = self.model.transcribe(
                    audio=audio_chunk_path,
                    initial_prompt=initial_prompt,
                    vad_filter=True,
                    word_timestamps=True,
                )
                for segment in segments:
                    aligned_segment = Segment(
                        start=chapter.start_time + segment.start,
                        end=chapter.start_time + segment.end,
                        text=segment.text,
                    )
                    chapter_segments.append(aligned_segment)
                    progress_bar.update(aligned_segment.end - current_timestamp)
                    current_timestamp = aligned_segment.end

                chaptered_transcriptions.append(
                    interfaces.ChapterTranscription(
                        title=chapter.title,
                        text="".join(segment.text for segment in chapter_segments),
                    )
                )

            if (
                current_timestamp < full_audio_duration
            ):  # silence at the end of the audio
                progress_bar.update(full_audio_duration - current_timestamp)

        return chaptered_transcriptions
