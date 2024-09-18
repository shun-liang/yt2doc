import re
import typing
import logging

import uuid
import ffmpeg

from pathlib import Path

from tqdm import tqdm
from pydantic import BaseModel

from yt_extractor.youtube import interfaces as youtube_interfaces
from yt_extractor.transcription import interfaces


logger = logging.getLogger(__file__)


class Segment(BaseModel):
    start: float
    end: float
    text: str


class WhisperPrompt(BaseModel):
    fictitious_prompt: str


class Transcriber:
    def __init__(
        self,
        temp_dir: Path,
        whisper_adapter: interfaces.IWhisperAdapter,
    ):
        self.temp_dir = temp_dir
        self.whisper_adapter = whisper_adapter

    @staticmethod
    def _clean_video_description(description: str) -> str:
        url_pattern = r"https?://\S+"
        timestamp_line_pattern = r"^\d+:\d+.*\n?"
        hashtag_pattern = r"#\w+"

        text = re.sub(
            f"{url_pattern}|{timestamp_line_pattern}|{hashtag_pattern}",
            "",
            description,
            flags=re.MULTILINE,
        )
        text = text.strip()
        text = re.sub(r"\n+| +", " ", text)
        text = text.replace(":", ".")
        return text

    def _get_initial_prompt(self, video_info: youtube_interfaces.YtVideoInfo) -> str:
        return f"{video_info.title}. {self._clean_video_description(description=video_info.description)}"

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
        audio_duration: float = float(ffmpeg.probe(audio_path)["format"]["duration"])
        rounded_audio_duration = round(audio_duration, 2)
        logger.info(f"Initial prompt: {initial_prompt}")
        segments = self.whisper_adapter.transcribe(
            audio_path=audio_path,
            initial_prompt=initial_prompt,
        )
        transcribed = ""
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
                progress_bar.update(rounded_audio_duration - current_timestamp)

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
        if len(video_info.chapters) > 0:
            chapters = video_info.chapters
        else:
            chapters = [
                youtube_interfaces.YtChapter(
                    title="Untitled chapter",
                    start_time=0.0,
                    end_time=full_audio_duration,
                )
            ]
        with tqdm(
            total=rounded_full_audio_duration,
            unit=" audio seconds",
            desc="Faster Whisper transcription",
        ) as progress_bar:
            for chapter in chapters:
                audio_chunk_path = self._get_audio_chunk_for_chapter(
                    audio_path=audio_path, chapter=chapter
                )

                chapter_segments: typing.List[Segment] = []

                segments = self.whisper_adapter.transcribe(
                    audio_path=audio_chunk_path,
                    initial_prompt=f"{initial_prompt} {chapter.title}",
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
