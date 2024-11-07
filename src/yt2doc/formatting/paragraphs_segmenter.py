import typing
import logging

from wtpsplit import SaT

from yt2doc.formatting import interfaces
from yt2doc.transcription import interfaces as transcription_interfaces

logger = logging.getLogger(__file__)


class ParagraphsSegmenter:
    def __init__(self, sat: SaT) -> None:
        self.sat = sat

    def segment(
        self, transcription_segments: typing.Sequence[transcription_interfaces.Segment]
    ) -> typing.List[typing.List[interfaces.Sentence]]:
        # Get sentences from SaT
        full_text = "".join(s.text for s in transcription_segments)
        logger.info("Splitting text into paragraphs with Segment Any Text.")
        paragraphed_texts = self.sat.split(
            full_text, do_paragraph_segmentation=True, verbose=True
        )

        # Align timestamps
        segments_text = "".join(s.text for s in transcription_segments)
        segments_pos = 0  # Position in segments text
        curr_segment_idx = 0  # Current segment index
        curr_segment_offset = 0  # Position within current segment

        result_paragraphs = []

        for paragraph in paragraphed_texts:
            result_sentences = []

            for sentence in paragraph:
                # Find matching position for this sentence
                sentence_pos = 0  # Position in current sentence

                # Find start position
                start_segment_idx = curr_segment_idx

                # Match characters exactly including spaces
                while sentence_pos < len(sentence):
                    if segments_pos >= len(segments_text):
                        break

                    # Match characters exactly
                    if sentence[sentence_pos] == segments_text[segments_pos]:
                        sentence_pos += 1
                        segments_pos += 1
                        curr_segment_offset += 1
                        # Update segment index if needed
                        while curr_segment_idx < len(
                            transcription_segments
                        ) - 1 and curr_segment_offset >= len(
                            transcription_segments[curr_segment_idx].text
                        ):
                            curr_segment_offset = 0
                            curr_segment_idx += 1
                    else:
                        # If no match, move forward in segments
                        segments_pos += 1
                        curr_segment_offset += 1
                        while curr_segment_idx < len(
                            transcription_segments
                        ) - 1 and curr_segment_offset >= len(
                            transcription_segments[curr_segment_idx].text
                        ):
                            curr_segment_offset = 0
                            curr_segment_idx += 1

                # Create sentence with aligned timestamp
                result_sentences.append(
                    interfaces.Sentence(
                        text=sentence,
                        start_second=transcription_segments[
                            start_segment_idx
                        ].start_second,
                    )
                )

            result_paragraphs.append(result_sentences)

        return result_paragraphs
