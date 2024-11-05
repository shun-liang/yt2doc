import re
import typing
import logging
import unicodedata

import uuid
import ffmpeg
import emoji

from pathlib import Path

from tqdm import tqdm

from yt2doc.media import interfaces as youtube_interfaces
from yt2doc.transcription import interfaces
from yt2doc.i18n import punctuations


logger = logging.getLogger(__file__)


class Transcriber:
    def __init__(
        self,
        temp_dir: Path,
        whisper_adapter: interfaces.IWhisperAdapter,
    ):
        self.temp_dir = temp_dir
        self.whisper_adapter = whisper_adapter

    @staticmethod
    def _clean_video_description(
        description: str, punctuations: punctuations.Punctuations
    ) -> str:
        url_pattern = r"https?://\S+"
        timestamp_min_sec_pattern = r"\d\d:\d\d"
        timestamp_hr_min_sec_pattern = r"\d\d:\d\d:\d\d"
        hashtag_pattern = r"#\w+"
        normalized_text = unicodedata.normalize("NFKD", description)

        text = re.sub(
            f"{url_pattern}|{timestamp_hr_min_sec_pattern}|{timestamp_min_sec_pattern}|{hashtag_pattern}",
            "",
            normalized_text,
            flags=re.MULTILINE,
        )
        text = text.strip()
        text = re.sub(r"\n+| +", punctuations.white_space, text)
        text = text.replace(":", punctuations.comma)
        text = emoji.replace_emoji(text, "")

        non_char_symbol_pattern = f"[^\\w\\s{punctuations.comma}{punctuations.full_stop}{punctuations.question_mark}{punctuations.exclamation_mark}]"
        text = re.sub(non_char_symbol_pattern, "", text, flags=re.UNICODE)

        text = re.sub(r"\s+", punctuations.white_space, text).strip()
        text = unicodedata.normalize("NFKC", text)

        return text

    @staticmethod
    def _clean_title(title: str, punctuations: punctuations.Punctuations) -> str:
        normalized_text = unicodedata.normalize("NFKD", title)
        non_char_symbol_pattern = f"[^\\w\\s{punctuations.comma}{punctuations.full_stop}{punctuations.question_mark}{punctuations.exclamation_mark}]"
        text = re.sub(non_char_symbol_pattern, "", normalized_text, flags=re.UNICODE)
        text = re.sub(r"\s+", punctuations.white_space, text).strip()
        text = unicodedata.normalize("NFKC", text)
        return text

    def _get_initial_prompt(
        self,
        language_code: str,
        media_info: youtube_interfaces.MediaInfo,
    ) -> str:
        punctuations_ = punctuations.get_punctuations(language_code=language_code)
        cleaned_title = self._clean_title(
            title=media_info.title,
            punctuations=punctuations_,
        )
        cleaned_video_description = self._clean_video_description(
            media_info.description, punctuations=punctuations_
        )
        chapter_titles = f"{punctuations_.comma}".join(
            c.title for c in media_info.chapters
        )
        return f"{cleaned_title}{punctuations_.full_stop} {cleaned_video_description} {chapter_titles}"

    def _get_audio_chunk_for_chapter(
        self, audio_path: Path, chapter: youtube_interfaces.MediaChapter
    ) -> Path:
        duration = chapter.end_time - chapter.start_time
        ext = audio_path.suffix
        file_path = self.temp_dir / f"{uuid.uuid4().hex}{ext}"
        ffmpeg.input(
            filename=audio_path.as_posix(), ss=chapter.start_time, t=duration
        ).output(file_path.as_posix()).run()
        return file_path

    def _fix_comma(self, segment_text: str, language_code: str) -> str:
        if language_code in ["zh"]:
            punctuations_ = punctuations.get_punctuations(language_code=language_code)
            return segment_text.replace(",", punctuations_.comma)
        return segment_text

    @staticmethod
    def _convert_audio_to_wav(audio_path: Path) -> Path:
        audio_format: str = ffmpeg.probe(audio_path)["format"]["format_name"]
        if audio_format == "wav":
            return audio_path

        wav_audio_path = audio_path.with_suffix(".wav")
        ffmpeg.input(audio_path.as_posix()).output(
            wav_audio_path.as_posix(), ar="16000", ac=1, acodec="pcm_s16le"
        ).overwrite_output().run()
        return wav_audio_path

    def transcribe(
        self, audio_path: Path, media_info: youtube_interfaces.MediaInfo
    ) -> interfaces.Transcription:
        wav_audio_path = self._convert_audio_to_wav(audio_path=audio_path)

        language_code = self.whisper_adapter.detect_language(audio_path=wav_audio_path)
        initial_prompt = self._get_initial_prompt(
            language_code=language_code,
            media_info=media_info,
        )
        logger.info(f"Initial prompt: {initial_prompt}")

        chaptered_transcriptions: typing.List[interfaces.ChapterTranscription] = []

        full_audio_duration: float = float(
            ffmpeg.probe(wav_audio_path)["format"]["duration"]
        )

        rounded_full_audio_duration = round(full_audio_duration, 2)
        current_timestamp = 0.0
        if len(media_info.chapters) > 0:
            chapters = media_info.chapters
        else:
            chapters = [
                youtube_interfaces.MediaChapter(
                    title="Untitled chapter",
                    start_time=0.0,
                    end_time=full_audio_duration,
                )
            ]
        with tqdm(
            total=rounded_full_audio_duration,
            unit=" audio seconds",
            desc="Transcription",
        ) as progress_bar:
            for chapter in chapters:
                audio_chunk_path = self._get_audio_chunk_for_chapter(
                    audio_path=wav_audio_path, chapter=chapter
                )

                chapter_segments: typing.List[interfaces.Segment] = []

                segments = self.whisper_adapter.transcribe(
                    audio_path=audio_chunk_path,
                    initial_prompt=initial_prompt,
                )
                for segment in segments:
                    aligned_segment = interfaces.Segment(
                        start_second=chapter.start_time + segment.start_second,
                        end_second=chapter.start_time + segment.end_second,
                        text=self._fix_comma(
                            segment_text=segment.text, language_code=language_code
                        ),
                    )
                    chapter_segments.append(aligned_segment)
                    progress_bar.update(aligned_segment.end_second - current_timestamp)
                    current_timestamp = aligned_segment.end_second

                chaptered_transcriptions.append(
                    interfaces.ChapterTranscription(
                        title=chapter.title,
                        segments=chapter_segments,
                    )
                )

            if (
                current_timestamp < full_audio_duration
            ):  # silence at the end of the audio
                progress_bar.update(full_audio_duration - current_timestamp)

        return interfaces.Transcription(
            language=language_code,
            chapters=chaptered_transcriptions,
        )
