import logging

from yt2doc.timer import Timer
from yt2doc.youtube import interfaces as youtube_interfaces
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction import interfaces

logger = logging.getLogger(__file__)


class Extractor:
    def __init__(
        self,
        video_info_extractor: youtube_interfaces.IYtVideoInfoExtractor,
        transcriber: transcription_interfaces.ITranscriber,
        file_cache: interfaces.IFileCache,
    ) -> None:
        self.yt_dlp_adapter = video_info_extractor
        self.transcriber = transcriber
        self.file_cache = file_cache

    def extract_by_chapter(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> interfaces.ChapteredTranscript:
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
            return interfaces.ChapteredTranscript(
                url=video_url,
                title=video_info.title,
                chapters=cached_chaptered_transcript,
                chaptered_at_source=len(video_info.chapters) > 0,
            )

        with Timer() as yt_dlp_timer:
            audio_path = self.yt_dlp_adapter.extract_audio(video_url=video_url)

        logger.info(f"Video download and convert time: {yt_dlp_timer.seconds} seconds")

        with Timer() as transcribe_timer:
            transcripts_by_chapter = [
                interfaces.TranscriptChapter(
                    title=chapter.title, segments=chapter.segments
                )
                for chapter in self.transcriber.transcribe(
                    audio_path=audio_path,
                    video_info=video_info,
                )
            ]

        logger.info(f"Transcription time: {transcribe_timer.seconds} seconds")

        self.file_cache.cache_chaptered_transcript(
            video_id=video_info.video_id,
            chapters=transcripts_by_chapter,
        )

        return interfaces.ChapteredTranscript(
            url=video_url,
            title=video_info.title,
            chapters=transcripts_by_chapter,
            chaptered_at_source=len(video_info.chapters) > 0,
        )

    def extract_playlist_by_chapter(
        self, playlist_url: str, skip_cache: bool
    ) -> interfaces.ChapteredTranscribedPlaylist:
        playlist_info = self.yt_dlp_adapter.extract_playlist_info(
            playlist_url=playlist_url
        )

        transcripts = [
            self.extract_by_chapter(video_url=video_url, skip_cache=skip_cache)
            for video_url in playlist_info.video_urls
        ]
        return interfaces.ChapteredTranscribedPlaylist(
            url=playlist_url,
            title=playlist_info.title,
            transcripts=transcripts,
        )
