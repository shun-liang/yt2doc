import typing
import logging

import jinja2

from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel
from slugify import slugify

from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class ParagraphToRender(BaseModel):
    start_h_m_s: str
    text: str


class ChapterToRender(BaseModel):
    title: str
    custom_id: str
    start_h_m_s: str
    paragraphs: typing.Sequence[ParagraphToRender]


class MarkdownFormatter:
    def __init__(
        self,
        paragraphs_segmenter: interfaces.IParagraphsSegmenter,
        to_timestamp_paragraphs: bool,
        add_table_of_contents: bool,
        topic_segmenter: typing.Optional[interfaces.ITopicSegmenter] = None,
    ) -> None:
        self.paragraphs_segmenter = paragraphs_segmenter
        self.topic_segmenter = topic_segmenter
        self.video_title_template = "# {name}"
        self.chapter_title_template = "## {name}"
        self.to_timestamp_paragraphs = to_timestamp_paragraphs
        self.add_table_of_contents = add_table_of_contents

    @staticmethod
    def _start_second_to_start_h_m_s(
        start_second: float, webpage_url_domain: str, video_id: str
    ) -> str:
        rounded_start_second = round(start_second)
        start_h_m_s = str(timedelta(seconds=rounded_start_second))
        if webpage_url_domain == "youtube.com":
            return (
                f"[{start_h_m_s}](https://youtu.be/{video_id}?t={rounded_start_second})"
            )
        return start_h_m_s

    def _render(
        self,
        title: str,
        chapters: typing.Sequence[interfaces.Chapter],
        video_url: str,
        video_id: str,
        webpage_url_domain: str,
    ) -> str:
        chapters_to_render: typing.List[ChapterToRender] = []
        for chapter in chapters:
            if len(chapter.paragraphs) == 0:
                continue

            paragraphs_to_render = [
                ParagraphToRender(
                    text=("".join([sentence.text for sentence in paragraph])).strip(),
                    start_h_m_s=self._start_second_to_start_h_m_s(
                        start_second=paragraph[0].start_second,
                        webpage_url_domain=webpage_url_domain,
                        video_id=video_id,
                    ),
                )
                for paragraph in chapter.paragraphs
            ]
            first_paragraph_to_render = paragraphs_to_render[0]
            chapters_to_render.append(
                ChapterToRender(
                    title=chapter.title,
                    custom_id=slugify(chapter.title),
                    start_h_m_s=first_paragraph_to_render.start_h_m_s,
                    paragraphs=paragraphs_to_render,
                )
            )

        current_dir = Path(__file__).parent
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(current_dir)
        )
        template = jinja_environment.get_template("template.md")
        rendered = template.render(
            title=title,
            chapters=[chapter.model_dump() for chapter in chapters_to_render],
            video_url=video_url,
            add_table_of_contents=self.add_table_of_contents,
            to_timestamp_paragraphs=self.to_timestamp_paragraphs,
        )
        return rendered

    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> interfaces.FormattedTranscript:
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

        else:
            chapters = [
                interfaces.Chapter(
                    title=chapter.title,
                    paragraphs=self.paragraphs_segmenter.segment(chapter.segments),
                )
                for chapter in chaptered_transcript.chapters
            ]

        rendered_transcript = self._render(
            title=chaptered_transcript.title,
            chapters=chapters,
            video_url=chaptered_transcript.url,
            video_id=chaptered_transcript.video_id,
            webpage_url_domain=chaptered_transcript.webpage_url_domain,
        )

        return interfaces.FormattedTranscript(
            title=chaptered_transcript.title,
            rendered_transcript=rendered_transcript,
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
