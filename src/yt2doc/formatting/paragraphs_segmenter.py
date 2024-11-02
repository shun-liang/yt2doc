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
        result: typing.List[typing.List[interfaces.Sentence]] = []
        
        # Character position trackers
        segment_char_pos = 0  # Position in concatenated transcription segments
        segment_idx = 0       # Current transcription segment
        segment_offset = 0    # Offset within current segment
        
        for paragraph in paragraphed_texts:
            paragraph_sentences: typing.List[interfaces.Sentence] = []
            
            for sentence_text in paragraph:
                if not sentence_text:
                    continue
                    
                sentence_start = segment_char_pos
                sentence_length = len(sentence_text)
                sentence_end = sentence_start + sentence_length
                
                # Find start segment and timestamp
                start_second = transcription_segments[segment_idx].start_second
                
                # Move through segments until we reach sentence end
                while segment_char_pos < sentence_end and segment_idx < len(transcription_segments):
                    current_segment = transcription_segments[segment_idx]
                    current_segment_length = len(current_segment.text)
                    
                    if segment_offset + (sentence_end - segment_char_pos) <= current_segment_length:
                        # Sentence ends in current segment
                        segment_char_pos += sentence_end - segment_char_pos
                        segment_offset += sentence_end - segment_char_pos
                        break
                    else:
                        # Move to next segment
                        remaining_length = current_segment_length - segment_offset
                        segment_char_pos += remaining_length
                        
                        if segment_idx + 1 < len(transcription_segments):
                            segment_idx += 1
                            segment_offset = 0
                        else:
                            # We've reached the end of segments
                            segment_char_pos = sentence_end  # Force exit from while loop
                            break
                
                # Use last segment's end time if we've reached the end
                end_second = transcription_segments[min(segment_idx, len(transcription_segments) - 1)].end_second
                
                aligned_sentence = interfaces.Sentence(
                    text=sentence_text,
                    start_second=start_second,
                    end_second=end_second
                )
                paragraph_sentences.append(aligned_sentence)
            
            if paragraph_sentences:
                result.append(paragraph_sentences)
                
        return result
