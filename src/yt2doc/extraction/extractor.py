import logging

from yt2doc.timer import Timer
from yt2doc.media import interfaces as youtube_interfaces
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction import interfaces

logger = logging.getLogger(__file__)


class Extractor:
    def __init__(
        self,
        media_info_extractor: youtube_interfaces.IYtMediaInfoExtractor,
        transcriber: transcription_interfaces.ITranscriber,
        file_cache: interfaces.IFileCache,
        ignore_source_chapters: bool,
    ) -> None:
        self.yt_dlp_adapter = media_info_extractor
        self.transcriber = transcriber
        self.file_cache = file_cache
        self.ignore_source_chapters = ignore_source_chapters

    def extract_by_chapter(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> interfaces.ChapteredTranscript:
        logger.info(f"Extracting video {video_url} by chapter.")

        media_info = self.yt_dlp_adapter.extract_media_info(video_url=video_url)

        if self.ignore_source_chapters:
            media_info.chapters = []

        if (
            not skip_cache
            and (
                cached_chaptered_transcript := self.file_cache.get_chaptered_transcript(
                    video_id=media_info.video_id
                )
            )
            is not None
        ):
            return cached_chaptered_transcript

        with Timer() as yt_dlp_timer:
            audio_path = self.yt_dlp_adapter.extract_audio(video_url=video_url)

        logger.info(f"Video download and convert time: {yt_dlp_timer.seconds} seconds")

        with Timer() as transcribe_timer:
            transcript = self.transcriber.transcribe(
                audio_path=audio_path,
                media_info=media_info,
            )
            transcripts_by_chapter = [
                interfaces.TranscriptChapter(
                    title=chapter.title, segments=chapter.segments
                )
                for chapter in transcript.chapters
            ]

        logger.info(f"Transcription time: {transcribe_timer.seconds} seconds")

        chaptered_transcript = interfaces.ChapteredTranscript(
            url=video_url,
            video_id=media_info.video_id,
            title=media_info.title,
            webpage_url_domain=media_info.webpage_url_domain,
            chapters=transcripts_by_chapter,
            chaptered_at_source=len(media_info.chapters) > 0,
            language=transcript.language,
        )

        self.file_cache.cache_chaptered_transcript(
            video_id=media_info.video_id,
            transcript=chaptered_transcript,
        )

        return chaptered_transcript

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
