import typing

from wtpsplit import SaT

from yt_extractor.extraction import interfaces


class Formatter:
    def __init__(self, sat: SaT) -> None:
        self.sat = sat

    def _paragraph_text(self, text: str) -> str:
        paragraphed_sentences: typing.List[typing.List[str]] = self.sat.split(
            text, do_paragraph_segmentation=True
        )
        paragraphs = ["".join(sentences) for sentences in paragraphed_sentences]
        paragraphed_text = "\n\n".join(paragraphs)
        return paragraphed_text

    @staticmethod
    def _get_video_and_chapter_title_templates(is_root: bool) -> tuple[str, str]:
        if is_root:
            return "# {name}", "## {name}"
        else:
            return "## {name}", "### {name}"

    def transcript_to_markdown(
        self, transcript: interfaces.Transcript, is_root: bool
    ) -> str:
        video_title_template, _ = self._get_video_and_chapter_title_templates(
            is_root=is_root
        )
        video_title = video_title_template.format(name=transcript.title)
        return f"{video_title}\n\n{transcript.url}\n\n{transcript}"

    def chaptered_transcript_to_markdown(
        self, chaptered_transcript: interfaces.ChapteredTranscript, is_root: bool
    ) -> str:
        video_title_template, chapter_title_template = (
            self._get_video_and_chapter_title_templates(is_root=is_root)
        )
        chapter_and_text_list: typing.List[typing.Tuple[str, str]] = []
        for chapter in chaptered_transcript.chapters:
            chapter_text = self._paragraph_text(chapter.text)
            chapter_and_text_list.append((chapter.title, chapter_text))

        transcript_text = "\n\n".join(
            [
                f"{chapter_title_template.format(name=chapter_title)}\n\n{chapter_text}"
                for chapter_title, chapter_text in chapter_and_text_list
            ]
        )
        return f"{video_title_template.format(name=chaptered_transcript.title)}\n\n{chaptered_transcript.url}\n\n{transcript_text}"

    def chaptered_playlist_transcripts_to_markdown(
        self, chaptered_playlist: interfaces.ChapteredTranscribedPlaylist
    ) -> str:
        playlist_title = f"# {chaptered_playlist.title}"

        formatted_transcripts = "\n\n".join(
            [
                self.chaptered_transcript_to_markdown(
                    chaptered_transcript=chaptered_transcript,
                    is_root=False,
                )
                for chaptered_transcript in chaptered_playlist.transcripts
            ]
        )

        return (
            f"{playlist_title}\n\n{chaptered_playlist.url}\n\n{formatted_transcripts}"
        )
