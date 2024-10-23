import pytest
from unittest.mock import MagicMock
from wtpsplit import SaT

from instructor import Instructor

from src.yt2doc.formatting.formatter import MarkdownFormatter
from src.yt2doc.formatting.llm_topic_segmenter import LLMTopicSegmenter
from src.yt2doc.extraction.interfaces import ChapteredTranscript, TranscriptChapter
from src.yt2doc.transcription.interfaces import Segment


@pytest.fixture
def mock_llm_client() -> Instructor:
    mock_llm_instance = MagicMock(spec=Instructor)
    return mock_llm_instance


def test_format_chaptered_transcript_basic() -> None:
    # Arrange
    sat = SaT("sat-3l")
    formatter = MarkdownFormatter(sat=sat)

    test_transcript = ChapteredTranscript(
        url="https://example.com/video",
        title="Test Video Title",
        language="en",
        chaptered_at_source=True,
        chapters=[
            TranscriptChapter(
                title="Chapter 1",
                segments=[
                    Segment(start=0.0, end=5.0, text="Sentence one is"),
                    Segment(start=5.0, end=10.0, text=" talking about something cool. Sentence"),
                    Segment(start=5.0, end=10.0, text=" two is talking something even cooler."),
                ],
            ),
            TranscriptChapter(
                title="Chapter 2",
                segments=[
                    Segment(start=10.0, end=15.0, text="Test paragraph 3."),
                    Segment(start=15.0, end=20.0, text="Test paragraph 4."),
                ],
            ),
        ],
    )

    # Act
    formatted_output = formatter.format_chaptered_transcript(
        chaptered_transcript=test_transcript
    )

    # Assert
    expected_output = """# Test Video Title

https://example.com/video

## Chapter 1

Test paragraph 1.

Test paragraph 2.

## Chapter 2

Test paragraph 3.

Test paragraph 4."""

    assert formatted_output.title == "Test Video Title"
    assert formatted_output.transcript == expected_output


def test_markdown_formatter_with_segmentation(mock_llm_client) -> None:
    # Arrange
    sat = SaT("sat-3l")
    segmenter = LLMTopicSegmenter(llm_client=mock_llm_client)
    formatter = MarkdownFormatter(sat=sat, topic_segmenter=segmenter)

    test_transcript = ChapteredTranscript(
        url="https://example.com/video",
        title="Test Video Title",
        language="en",
        chaptered_at_source=False,
        chapters=[
            TranscriptChapter(
                title="Chapter 1",
                segments=[
                    Segment(start=0.0, end=5.0, text="Test paragraph 1."),
                    Segment(start=5.0, end=10.0, text="Test paragraph 2."),
                ],
            )
        ],
    )

    # Configure mock LLM response
    mock_llm_client.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"chapters": [{"title": "Introduction", "text": "Test paragraph 1."}, {"title": "Discussion", "text": "Test paragraph 2."}]}'
                )
            )
        ]
    )

    # Act
    formatted_output = formatter.format_chaptered_transcript(
        chaptered_transcript=test_transcript
    )

    # Assert
    assert "# Test Video Title" in formatted_output.transcript
    assert "## Introduction" in formatted_output.transcript
    assert "## Discussion" in formatted_output.transcript
    assert "Test paragraph 1." in formatted_output.transcript
    assert "Test paragraph 2." in formatted_output.transcript
    mock_llm_client.chat.completions.create.assert_called_once()
