import typing
import logging

from dataclasses import dataclass

from yt_extractor.yt_dlp_adapter import YtDlpAdapter
from yt_extractor.whisper_adapter import WhisperAdapter
from yt_extractor.file_cache import FileCache
from yt_extractor.timer import Timer

logger = logging.getLogger(__file__)

MetaDict = typing.Dict[str, typing.Union[str, int, float]]


@dataclass
class Transcript:
    url: str
    title: str
    text: str


class TranscriptChapter(typing.Protocol):
    title: str
    text: str


@dataclass
class ChapteredTranscript:
    url: str
    title: str
    chapters: typing.Sequence[TranscriptChapter]


@dataclass
class TranscribedPlaylist:
    url: str
    title: str
    transcripts: typing.Sequence[Transcript]


class ChapteredTranscriptProtocol(typing.Protocol):
    url: str
    title: str
    chapters: typing.Sequence[TranscriptChapter]


@dataclass
class ChapteredTranscribedPlaylist:
    url: str
    title: str
    transcripts: typing.Sequence[ChapteredTranscriptProtocol]


class TranscriptExtractor:
    def __init__(
        self,
        yt_dlp_adapter: YtDlpAdapter,
        whisper_adapter: WhisperAdapter,
        file_cache: FileCache,
        meta: MetaDict,
    ) -> None:
        self.yt_dlp_adapter = yt_dlp_adapter
        self.whisper_adapter = whisper_adapter
        self.file_cache = file_cache
        self.meta = meta

    def extract(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> Transcript:
        video_info = self.yt_dlp_adapter.extract_video_info(video_url=video_url)
        if (
            not skip_cache
            and (
                cached_transcript := self.file_cache.get_transcript(
                    video_id=video_info.video_id
                )
            )
            is not None
        ):
            return Transcript(
                url=video_url, title=video_info.title, text=cached_transcript
            )

        with Timer() as yt_dlp_timer:
            audio_path = self.yt_dlp_adapter.extract_audio(video_url=video_url)

        logger.info(f"Video download and convert time: {yt_dlp_timer.seconds} seconds")

        with Timer() as transcribe_timer:
            transcript = self.whisper_adapter.transcribe_full_text(
                audio_path=audio_path
            )

        logger.info(f"Transcription time: {transcribe_timer.seconds} seconds")

        self.file_cache.cache_transcript(
            video_id=video_info.video_id, transcript=transcript, meta=self.meta
        )
        return Transcript(url=video_url, title=video_info.title, text=transcript)

    def extract_by_chapter(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> ChapteredTranscript:
        logger.info(f"Extracting video {video_url} by chapter.")

        video_info = self.yt_dlp_adapter.extract_video_info(video_url=video_url)
        if (
            not skip_cache
            and (
                cached_chaptered_transcript := self.file_cache.get_chaptered_transcript(
                    video_id=video_info.video_id
                )
            )
            is not None
        ):
            return ChapteredTranscript(
                url=video_url,
                title=video_info.title,
                chapters=cached_chaptered_transcript,
            )

        with Timer() as yt_dlp_timer:
            audio_path = self.yt_dlp_adapter.extract_audio(video_url=video_url)

        logger.info(f"Video download and convert time: {yt_dlp_timer.seconds} seconds")

        with Timer() as transcribe_timer:
            transcripts_by_chapter = self.whisper_adapter.transcribe_by_chapter(
                audio_path=audio_path,
                title=video_info.title,
                chapters=video_info.chapters,
            )

        logger.info(f"Transcription time: {transcribe_timer.seconds} seconds")

        self.file_cache.cache_chaptered_transcript(
            video_id=video_info.video_id,
            chapters=transcripts_by_chapter,
            meta=self.meta,
        )

        return ChapteredTranscript(
            url=video_url, title=video_info.title, chapters=transcripts_by_chapter
        )

    def extract_playlist_by_chapter(
        self, playlist_url: str, skip_cache: bool
    ) -> ChapteredTranscribedPlaylist:
        playlist_info = self.yt_dlp_adapter.extract_playlist_info(
            playlist_url=playlist_url
        )

        transcripts = [
            self.extract_by_chapter(video_url=video_url, skip_cache=skip_cache)
            for video_url in playlist_info.video_urls
        ]
        return ChapteredTranscribedPlaylist(
            url=playlist_url,
            title=playlist_info.title,
            transcripts=transcripts,
        )
