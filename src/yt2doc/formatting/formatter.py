import typing
import logging

from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class MarkdownFormatter:
    def __init__(
        self,
        paragraphs_segmenter: interfaces.IParagraphsSegmenter,
        # timestamp_paragraphs: bool,
        topic_segmenter: typing.Optional[interfaces.ITopicSegmenter] = None,
    ) -> None:
        self.paragraphs_segmenter = paragraphs_segmenter
        self.topic_segmenter = topic_segmenter
        self.video_title_template = "# {name}"
        self.chapter_title_template = "## {name}"
        # self.timestamp_paragraphs = timestamp_paragraphs

    @staticmethod
    def _paragraphs_to_text(
        paragraphs: typing.Sequence[typing.Sequence[interfaces.Sentence]],
        # timestamp_paragraphs: bool,
        # webpage_url: str,
        # webpage_url_domain: str,
    ) -> str:
        paragraph_texts = []
        for paragraph in paragraphs:
            first_sentence = paragraph[0]
            paragraph_text = "".join(sentence.text for sentence in paragraph)
            # if timestamp_paragraphs:
            #     if webpage_url_domain == "youtube.com":
            #         timestamp_prefix = "[\({}\)]()"
            paragraph_texts.append(paragraph_text)
        return "\n\n".join(paragraph_texts)

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
            paragraphed_sentences = self.paragraphs_segmenter.segment(
                transcription_segments=transcript_segments
            )
            chapters = self.topic_segmenter.segment(
                sentences_in_paragraphs=paragraphed_sentences
            )
            chapter_and_text_list = [
                (chapter.title, self._paragraphs_to_text(chapter.paragraphs))
                for chapter in chapters
            ]

        else:
            for chapter in chaptered_transcript.chapters:
                paragraphed_sentences = self.paragraphs_segmenter.segment(
                    transcription_segments=chapter.segments
                )
                chapter_full_text = self._paragraphs_to_text(
                    paragraphs=paragraphed_sentences
                )
                chapter_and_text_list.append((chapter.title, chapter_full_text.strip()))

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
