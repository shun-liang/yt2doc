import typing

from wtpsplit import SaT

from yt_extractor.extraction import interfaces as extraction_interfaces
from yt_extractor.formatting import interfaces


class MarkdownFormatter:
    def __init__(self, sat: SaT) -> None:
        self.sat = sat
        self.video_title_template = "# {name}"
        self.chapter_title_template = "## {name}"

    def _paragraph_text(self, text: str) -> str:
        paragraphed_sentences: typing.List[typing.List[str]] = self.sat.split(
            text, do_paragraph_segmentation=True
        )
        paragraphs = ["".join(sentences) for sentences in paragraphed_sentences]
        paragraphed_text = "\n\n".join(paragraphs)
        return paragraphed_text

    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> interfaces.FormattedTranscript:
        chapter_and_text_list: typing.List[typing.Tuple[str, str]] = []
        for chapter in chaptered_transcript.chapters:
            chapter_text = self._paragraph_text(chapter.text)
            chapter_and_text_list.append((chapter.title, chapter_text))

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