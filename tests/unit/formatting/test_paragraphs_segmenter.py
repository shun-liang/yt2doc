from unittest.mock import Mock

from wtpsplit import SaT

from yt2doc.formatting.paragraphs_segmenter import ParagraphsSegmenter
from yt2doc.transcription.interfaces import Segment


def test_segment_aligns_timestamps_correctly():
    # Mock SaT to return known sentence splits
    mock_sat = Mock(spec=SaT)
    mock_sat.split.return_value = [
        [
            "Hello world! ",  # First paragraph, first sentence
            "This is a test. "  # First paragraph, second sentence
        ],
        [
            "Another paragraph here. "  # Second paragraph, single sentence
        ]
    ]
    
    # Create test transcription segments that split text differently
    segments = [
        Segment(start_second=0.0, end_second=1.0, text="Hello"),
        Segment(start_second=1.0, end_second=2.0, text=" world! This"),
        Segment(start_second=2.0, end_second=3.0, text=" is a"),
        Segment(start_second=3.0, end_second=4.0, text=" test. Another"),
        Segment(start_second=4.0, end_second=5.0, text=" paragraph"),
        Segment(start_second=5.0, end_second=6.0, text=" here. ")
    ]
    
    segmenter = ParagraphsSegmenter(mock_sat)
    result = segmenter.segment(segments)
    
    # Verify structure: should be sequence of paragraphs containing sequences of sentences
    assert len(result) == 2  # Two paragraphs
    assert len(result[0]) == 2  # First paragraph has two sentences
    assert len(result[1]) == 1  # Second paragraph has one sentence
    
    # Verify first paragraph, first sentence
    assert result[0][0].text == "Hello world! "
    assert result[0][0].start_second == 0.0  # Starts at first segment
    assert result[0][0].end_second == 2.0    # Ends at second segment
    
    # Verify first paragraph, second sentence
    assert result[0][1].text == "This is a test. "
    assert result[0][1].start_second == 1.0  # Starts at third segment
    assert result[0][1].end_second == 4.0    # Ends at fourth segment
    
    # Verify second paragraph, single sentence
    assert result[1][0].text == "Another paragraph here. "
    assert result[1][0].start_second == 4.0  # Starts at fifth segment
    assert result[1][0].end_second == 6.0    # Ends at last segment
    
    # Verify SaT was called correctly
    mock_sat.split.assert_called_once_with(
        "Hello world! This is a test. Another paragraph here. ",
        do_paragraph_segmentation=True,
        verbose=True
    )
