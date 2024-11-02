import typing

from wtpsplit import SaT

from src.yt2doc.formatting import interfaces
from yt2doc.transcription import interfaces as transcription_interfaces


class ParagraphsSegmenter:
    def __init__(self, sat: SaT) -> None:
        self.sat = sat

    def segment(
        self, transcription_segments: typing.Sequence[transcription_interfaces.Segment]
    ) -> typing.Sequence[typing.Sequence[interfaces.Sentence]]:
        transcription_segment_texts = [s.text for s in transcription_segments]
        full_text = "".join(transcription_segment_texts)
        paragraphed_texts: typing.List[typing.List[str]] = self.sat.split(
            full_text, do_paragraph_segmentation=True, verbose=True
        )

        # Paragraph-Transcription Segment timestamp alignment

