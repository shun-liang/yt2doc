import logging

from yt2doc.timer import Timer
from yt2doc.youtube import interfaces as youtube_interfaces
from yt2doc.formatting import interfaces as formatting_interfaces
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction import interfaces as extraction_interfaces

logger = logging.getLogger(__file__)


class Yt2Doc:
    def __init__(
        self,
        video_info_extractor: youtube_interfaces.IYtVideoInfoExtractor,
        transcriber: transcription_interfaces.ITranscriber,
        formatter: formatting_interfaces.IFormatter,
        file_cache: extraction_interfaces.IFileCache,
    ) -> None:
        self.video_info_extractor = video_info_extractor
        self.transcriber = transcriber
        self.formatter = formatter
        self.file_cache = file_cache

    def video_to_document(
        self, video_url: str, skip_cache: bool = False
    ) -> formatting_interfaces.FormattedTranscript:
        logger.info(f"extracting video {video_url}")

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
            return extraction_interfaces.ChapteredTranscript(
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
                extraction_interfaces.TranscriptChapter(
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

        formatted_transcript = self.formatter.format_chaptered_transcript(
            chaptered_transcript=transcript_by_chapter
        )
        return formatted_transcript

    def playlist_to_documents(
        self, playlist_url: str, skip_cache: bool = False
    ) -> formatting_interfaces.FormattedPlaylist:
        logger.info(f"extracting playlist {playlist_url}")
        chaptered_transcribed_playlist = self.extractor.extract_playlist_by_chapter(
            playlist_url=playlist_url, skip_cache=skip_cache
        )
        formatted_playlist = self.formatter.format_chaptered_playlist_transcripts(
            chaptered_playlist=chaptered_transcribed_playlist
        )
        return formatted_playlist
