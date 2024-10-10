import typing
import logging

from wtpsplit import SaT

from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class MarkdownFormatter:
    def __init__(
        self,
        sat: SaT,
        topic_segmenter: typing.Optional[interfaces.ITopicSegmenter] = None,
    ) -> None:
        self.sat = sat
        self.topic_segmenter = topic_segmenter
        self.video_title_template = "# {name}"
        self.chapter_title_template = "## {name}"

    def _paragraph_text(self, text: str) -> str:
        if len(text) < 15:
            return text
        logger.info("Splitting text into paragraphs with Segment Any Text.")
        paragraphed_sentences: typing.List[typing.List[str]] = self.sat.split(
            text, do_paragraph_segmentation=True, verbose=True
        )
        paragraphs = ["".join(sentences) for sentences in paragraphed_sentences]
        paragraphed_text = "\n\n".join(paragraphs)
        return paragraphed_text

    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> interfaces.FormattedTranscript:
        chapter_and_text_list: typing.List[typing.Tuple[str, str]] = []

        if (
            self.topic_segmenter is not None
            and not chaptered_transcript.chaptered_at_source
            and len(chaptered_transcript.chapters) == 1
        ):
            transcript_segments = chaptered_transcript.chapters[0].segments
            full_text = "".join([segment.text for segment in transcript_segments])
            logger.info(
                "Splitting text into paragraphs with Segment Any Text for topic segmentation."
            )
            paragraphed_sentences: typing.List[typing.List[str]] = self.sat.split(
                full_text, do_paragraph_segmentation=True, verbose=True
            )
            chapters = self.topic_segmenter.segment(paragraphs=paragraphed_sentences)
            chapter_and_text_list = [
                (chapter.title, chapter.text) for chapter in chapters
            ]

        else:
            for chapter in chaptered_transcript.chapters:
                chapter_text = self._paragraph_text(
                    "".join(s.text for s in chapter.segments)
                )
                chapter_and_text_list.append((chapter.title, chapter_text.strip()))

        transcript_text = "\n\n".join(
            [
                f"{self.chapter_title_template.format(name=chapter_title)}\n\n{chapter_text}"
                for chapter_title, chapter_text in chapter_and_text_list
            ]
        )
        transcript_text = f"{self.video_title_template.format(name=chaptered_transcript.title)}\n\n{chaptered_transcript.url}\n\n{transcript_text}"
        return interfaces.FormattedTranscript(
            title=chaptered_transcript.title,
            transcript=transcript_text,
        )

    def format_chaptered_playlist_transcripts(
        self, chaptered_playlist: extraction_interfaces.ChapteredTranscribedPlaylist
    ) -> interfaces.FormattedPlaylist:
        playlist_title = f"# {chaptered_playlist.title}"

        transcripts = [
            self.format_chaptered_transcript(chaptered_transcript=chaptered_transcript)
            for chaptered_transcript in chaptered_playlist.transcripts
        ]

        return interfaces.FormattedPlaylist(
            title=playlist_title, transcripts=transcripts
        )
