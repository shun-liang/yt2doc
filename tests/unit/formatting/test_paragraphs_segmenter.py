from unittest.mock import Mock

from wtpsplit import SaT

from src.yt2doc.formatting.paragraphs_segmenter import ParagraphsSegmenter
from src.yt2doc.transcription.interfaces import Segment


def test_segment_aligns_timestamps_correctly() -> None:
    # Mock SaT to return known sentence splits
    mock_sat = Mock(spec=SaT)
    mock_sat.split.return_value = [
        [
            "Hello world! ",  # First paragraph, first sentence
            "This is a test. ",  # First paragraph, second sentence
        ],
        [
            "Another paragraph here. ",  # Second paragraph, single sentence
            "Only 0.1 percent people get it. ",
            "And even more. ",  # Second paragraph, third sentence
        ],
        [
            "This is a longer sentence that spans multiple segments and tests our handling of longer text blocks. "  # Third paragraph
        ],
        [
            "Short text. ",  # Fourth paragraph, first sentence
            "Followed by another. ",  # Fourth paragraph, second sentence
            "And one more for good measure. ",  # Fourth paragraph, third sentence
        ],
        [
            "Final paragraph to conclude our test. ",  # Fifth paragraph, first sentence
            "With some extra content. ",  # Fifth paragraph, second sentence
            "And a final closing statement. ",  # Fifth paragraph, third sentence
        ],
    ]

    # Create test transcription segments that split text differently
    segments = [
        Segment(start_second=0.0, end_second=1.0, text=" Hello"),
        Segment(start_second=1.0, end_second=2.0, text=" world! This"),
        Segment(start_second=2.0, end_second=3.0, text=" is a"),
        Segment(start_second=3.0, end_second=4.0, text=" test. Another"),
        Segment(start_second=4.0, end_second=5.0, text=" paragraph here. Only"),
        Segment(
            start_second=5.0, end_second=6.0, text=" 0.1 percent people get it. And"
        ),
        Segment(start_second=6.0, end_second=7.0, text=" even more. This is a"),
        Segment(start_second=7.0, end_second=8.0, text=" longer sentence that spans"),
        Segment(start_second=8.0, end_second=9.0, text=" multiple segments and tests"),
        Segment(start_second=9.0, end_second=10.0, text=" our handling of longer"),
        Segment(start_second=10.0, end_second=11.0, text=" text blocks. Short"),
        Segment(start_second=11.0, end_second=12.0, text=" text. Followed by"),
        Segment(start_second=12.0, end_second=13.0, text=" another. And one"),
        Segment(
            start_second=13.0, end_second=14.0, text=" more for good measure. Final"
        ),
        Segment(start_second=14.0, end_second=15.0, text=" paragraph to conclude our"),
        Segment(start_second=15.0, end_second=16.0, text=" test. With some extra"),
        Segment(start_second=16.0, end_second=17.0, text=" content. And a final"),
        Segment(start_second=17.0, end_second=18.0, text=" closing statement."),
    ]

    segmenter = ParagraphsSegmenter(mock_sat)
    result = segmenter.segment(segments)

    # Verify structure: should be sequence of paragraphs containing sequences of sentences
    assert len(result) == 5  # Five paragraphs
    assert len(result[0]) == 2  # First paragraph has two sentences
    assert len(result[1]) == 3  # Second paragraph has three sentences
    assert len(result[2]) == 1  # Third paragraph has one sentence
    assert len(result[3]) == 3  # Fourth paragraph has three sentences
    assert len(result[4]) == 3  # Fifth paragraph has three sentences

    # Verify first paragraph
    assert result[0][0].text == "Hello world! "
    assert result[0][0].start_second == 0.0

    assert result[0][1].text == "This is a test. "
    assert result[0][1].start_second == 1.0

    # Verify second paragraph
    assert result[1][0].text == "Another paragraph here. "
    assert result[1][0].start_second == 3.0

    assert result[1][1].text == "Only 0.1 percent people get it. "
    assert result[1][1].start_second == 4.0

    assert result[1][2].text == "And even more. "
    assert result[1][2].start_second == 5.0

    # Verify third paragraph (long sentence spanning multiple segments)
    assert (
        result[2][0].text
        == "This is a longer sentence that spans multiple segments and tests our handling of longer text blocks. "
    )
    assert result[2][0].start_second == 6.0

    # Verify fourth paragraph
    assert result[3][0].text == "Short text. "
    assert result[3][0].start_second == 10.0

    assert result[3][1].text == "Followed by another. "
    assert result[3][1].start_second == 11.0

    assert result[3][2].text == "And one more for good measure. "
    assert result[3][2].start_second == 12.0

    # Verify fifth paragraph
    assert result[4][0].text == "Final paragraph to conclude our test. "
    assert result[4][0].start_second == 13.0

    assert result[4][1].text == "With some extra content. "
    assert result[4][1].start_second == 15.0

    assert result[4][2].text == "And a final closing statement. "
    assert result[4][2].start_second == 16.0

    # Verify SaT was called correctly with complete text
    mock_sat.split.assert_called_once_with(
        " Hello world! This is a test. Another paragraph here. Only 0.1 percent people get it. "
        "And even more. This is a longer sentence that spans multiple segments and tests "
        "our handling of longer text blocks. Short text. Followed by another. And one "
        "more for good measure. Final paragraph to conclude our test. With some extra "
        "content. And a final closing statement.",
        do_paragraph_segmentation=True,
        verbose=True,
    )
