import logging

from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.formatting import interfaces as formatting_interfaces

logger = logging.getLogger(__file__)


class Yt2Doc:
    def __init__(
        self,
        extractor: extraction_interfaces.IExtractor,
        formatter: formatting_interfaces.IFormatter,
    ) -> None:
        self.extractor = extractor
        self.formatter = formatter

    def video_to_document(
        self, video_url: str, skip_cache: bool = False
    ) -> formatting_interfaces.FormattedTranscript:
        logger.info(f"extracting video {video_url}")

        transcript_by_chapter = self.extractor.extract_by_chapter(
            video_url=video_url, skip_cache=skip_cache
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
