import typing

from wtpsplit import SaT

from yt2doc.formatting import interfaces
from yt2doc.transcription import interfaces as transcription_interfaces


class ParagraphsSegmenter:
    def __init__(self, sat: SaT) -> None:
        self.sat = sat

    def segment(
        self, transcription_segments: typing.Sequence[transcription_interfaces.Segment]
    ) -> typing.Sequence[typing.Sequence[interfaces.Sentence]]:
        # Get sentences from SaT
        full_text = "".join(s.text for s in transcription_segments)
        paragraphed_texts = self.sat.split(full_text, do_paragraph_segmentation=True, verbose=True)

        # Find which segment contains each sentence's start/end
        result = []
        text_pos = 0
        
        for paragraph in paragraphed_texts:
            sentences = []
            for sentence in paragraph:
                if not sentence:
                    continue

                # Find start segment
                start_idx = 0
                pos = text_pos
                while start_idx < len(transcription_segments):
                    if pos < len(transcription_segments[start_idx].text):
                        break
                    pos -= len(transcription_segments[start_idx].text)
                    start_idx += 1

                # If sentence starts after a period, use next segment's start time
                start_time = transcription_segments[start_idx].start_second
                if pos > 0 and transcription_segments[start_idx].text[:pos].strip().endswith('.'):
                    start_time = transcription_segments[min(start_idx + 1, len(transcription_segments) - 1)].start_second

                # Find end segment
                end_idx = start_idx
                remaining = len(sentence)
                pos = pos
                while remaining > 0 and end_idx < len(transcription_segments):
                    segment_remaining = len(transcription_segments[end_idx].text) - pos
                    if remaining <= segment_remaining:
                        break
                    remaining -= segment_remaining
                    pos = 0
                    end_idx += 1

                sentences.append(interfaces.Sentence(
                    text=sentence,
                    start_second=start_time,
                    end_second=transcription_segments[end_idx].end_second
                ))
                text_pos += len(sentence)

            if sentences:
                result.append(sentences)

        return result
