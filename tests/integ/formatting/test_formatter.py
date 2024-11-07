import re
import typing

import pytest

from unittest.mock import MagicMock
from wtpsplit import SaT


from src.yt2doc.formatting.formatter import MarkdownFormatter
from src.yt2doc.formatting.llm_topic_segmenter import LLMTopicSegmenter
from src.yt2doc.formatting.llm_adapter import LLMAdapter
from src.yt2doc.formatting.paragraphs_segmenter import ParagraphsSegmenter
from src.yt2doc.extraction.interfaces import ChapteredTranscript, TranscriptChapter
from src.yt2doc.transcription.interfaces import Segment


def time_to_seconds(time_str: str) -> float:
    h, m, s = time_str.split(":")
    seconds = int(h) * 3600 + int(m) * 60 + float(s)
    return round(seconds, 2)


def parse_whisper_line(line: str) -> Segment:
    pattern = r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s{2}(.*)"
    match = re.match(pattern, line)
    if match:
        start_time, end_time, text = match.groups()
        return Segment(
            start_second=time_to_seconds(start_time),
            end_second=time_to_seconds(end_time),
            text=text,
        )
    assert False, "Line does not match expected whisper segment pattern."


@pytest.fixture
def mock_llm_adapter() -> LLMAdapter:
    return MagicMock(spec_set=LLMAdapter)


@pytest.fixture
def mock_transcript_segments() -> typing.List[Segment]:
    transcript_plain_text = """[00:00:00.000 --> 00:00:15.640]   Hi class. So today I'll be talking about climate change and species responses to climate change,
[00:00:15.640 --> 00:00:19.500]   and what I'll be showing you today is what we can learn from the geological record in terms of
[00:00:19.500 --> 00:00:23.420]   understanding past climatic events and how a species responded to those climatic events.
[00:00:23.420 --> 00:00:28.540]   All right, so the first context here, and this could be a lecture into itself, which I'm not
[00:00:28.540 --> 00:00:32.340]   going to go into right now, is the point that the world is warming and that humans are responsible
[00:00:32.340 --> 00:00:35.760]   for it. There's been a lot of debate about this in the public media, but again I want to hit the
[00:00:35.760 --> 00:00:40.700]   point that scientists are unified on this one. The evidence is overwhelming at this point that the
[00:00:40.700 --> 00:00:45.260]   world is warming and humans are responsible. So you look at the plot there, you can see the black line
[00:00:45.260 --> 00:00:51.460]   which shows historical observations of global mean temperatures over the last century. You can see
[00:00:51.460 --> 00:00:55.920]   there's been about a seven-tenths of a degree of warming. Now if you look to the future, which is
[00:00:55.920 --> 00:01:01.080]   those various blue lines, you can see that the various models project an acceleration of these
[00:01:01.080 --> 00:01:05.960]   warming trends over this century. And depending on the scenario you look at, from blue to red there,
[00:01:05.960 --> 00:01:09.920]   you can have anywhere from about a two-degree warming to about a four-degree warming. Now you can
[00:01:09.920 --> 00:01:13.860]   ignore that yellow-red line at the bottom there. That's more of a what-if scenario. If we were to
[00:01:13.860 --> 00:01:19.700]   do, if we were to shut down CO2 and other greenhouse gases emissions immediately, what would happen to the climate
[00:01:19.700 --> 00:01:24.060]   system, which is clearly not going to happen anytime soon. So the point being that we are facing
[00:01:24.060 --> 00:01:29.220]   two to four-degree warming over the century, and the question then being what will happen? How will the
[00:01:29.220 --> 00:01:34.100]   physical systems respond in terms of hurricane frequency, flood frequency? How will species and
[00:01:34.100 --> 00:01:39.220]   natural ecosystems respond? And how will our own societies respond to these drastic changes in climate?
[00:01:39.220 --> 00:01:44.380]   So one place we can learn to look to answer these sort of questions is looking to the last 20,000 years or so. If you look at that map at the top, what you can see there is that 20,000 years ago we had a large ice sheet on top of the northern hemisphere, covering much of North America and the rest of the northern hemisphere, contrasted with the map right there, which shows that ice, which is more the present-day state, ice being confined mainly to Greenlands. We've gone from a glacial state to an interglacial state in the span of about 20,000 years. That red curve at bottom,
[00:01:44.380 --> 00:01:59.540]   shows that we've gone from about a 10-degree change in Greenland, this is the temperature record from Greenland, this is the temperature record from Greenland, this is the temperature record, which we've gone from a glacial state to an interglacial state, which we've gone from a glacial state to an interglacial state in the span of about 20,000 years.
[00:01:59.540 --> 00:02:22.500]   That red curve at bottom shows that we've gone from a glacial state in the span of about 20,000 years. That red curve at bottom shows that we've gone from about a 10-degree change in Greenland, this is the temperature record from Greenland, we go from about, at left 20,000 years ago to right, present day, you can see several abrupt warming and coolings along the way, these abrupt transitional events.
[00:02:22.700 --> 00:02:30.320]   And so we have a very good geological record and understanding of the climatic changes of the past, and so now we can look at the ecological responses to those climatic changes.
[00:02:30.320 --> 00:02:42.820]   So what are some of the things we can pull out from these sorts of data? When we look at fossil pollen and other plant records, one of the things we can see is that species ranges are highly dynamic. As climate changes, species migrate.
[00:02:42.820 --> 00:02:51.400]   You can see this here, where you can see at the top there, the left-hand panel is for 21,000 years ago, going to the right at present.
[00:02:51.820 --> 00:03:00.580]   And you can see how ice melts away as you go from map to map there. But then look at the green, which is the distribution of spruce based upon fossil pollen and other fossil plant records.
[00:03:00.580 --> 00:03:07.860]   You can see how the distribution of spruce has changed from being mainly in the eastern U.S. to being across Canada over the span of these 20,000 years.
[00:03:07.860 --> 00:03:18.600]   So ranges are highly dynamic. Now, of course, trees aren't picking up and moving. They're not walking from point A to point B, but instead, they're dispersing seeds. Some of these seeds establish in new areas.
[00:03:19.260 --> 00:03:28.020]   They can colonize and establish new populations. And in other areas where spruce used to grow, those areas become unfavorable and those populations die off.
[00:03:28.020 --> 00:03:31.020]   So that's how we have these range shifts of these species.
[00:03:31.020 --> 00:03:39.780]   Now, a piece of good news in the geological record is that we don't have very many observed extinctions of plants of the last 20,000 years. Plant species, I should say.
[00:03:39.780 --> 00:03:50.540]   One example of where we do is shown here in this diagram. This is some cross-sections of some spruce needles. The first four A through D are from still living species of spruce.
[00:03:50.540 --> 00:04:02.540]   E through G are from extinct species of spruce. And so there's some clear evidence from fossil records in the Lake Glacial that there's a set of spruce species that grew in the past that are not found today.
[00:04:02.540 --> 00:04:20.540]   So species do go extinct. But this is more the exception than the rule. However, if you combine climate change with other drivers, other stressors to these natural systems, that's when you can have widespread and potentially devastating waves of extinction.
[00:04:20.540 --> 00:04:33.540]   The most famous ones occur again at the Pleistocene here with the extinction of mammoths and other large mammals from North America. These were caused by the combination of climate change with human hunting.
[00:04:33.540 --> 00:04:41.540]   And so it wasn't just climate change alone that killed the mammoths. It wasn't just human hunting alone that killed the mammoths. But it was a combination together that was so deadly.
[00:04:41.540 --> 00:04:56.540]   So one of the clear lessons for today is that as we go in this 21st century, it's a combination of climate change with human land use, with changes to nutrient cycles, with invasive species being moved from continent to continent, that are going to pose a true risk to species at present.
[00:04:56.540 --> 00:05:03.540]   The last point I want to hit is, is these 21st century warmings a big deal? Three to five degrees Celsius. What's the big deal about that?
[00:05:03.540 --> 00:05:15.540]   Well this plot places the 21st century warm in the context of what we've seen in the geological record. The horizontal axis is rate of change. The vertical axis is magnitude of change.
[00:05:15.540 --> 00:05:22.540]   The point I want to draw your attention to is that the red ellipse is what's projected for the 21st century. The green ellipses are various geological events.
[00:05:22.540 --> 00:05:29.540]   And the point there is that the 21st century warming is unusual because it's both got the highest rate of change and the largest magnitude of change.
[00:05:29.540 --> 00:05:36.540]   And so there's definite reason in this geological context to be concerned about what's coming for this century. Thank you.
[00:05:36.540 --> 00:05:37.540]   Thank you.
[00:05:37.540 --> 00:05:38.700]   Thank you."""

    return [parse_whisper_line(line) for line in transcript_plain_text.splitlines()]


def test_format_chaptered_transcript_basic(
    mock_transcript_segments: typing.List[Segment],
) -> None:
    # Arrange
    sat = SaT("sat-3l")
    paragraphs_segmenter = ParagraphsSegmenter(sat=sat)
    formatter = MarkdownFormatter(
        paragraphs_segmenter=paragraphs_segmenter, to_timestamp_paragraphs=False
    )

    segments_dicts = [
        {
            "start_second": segment.start_second,
            "end_second": segment.end_second,
            "text": segment.text,
        }
        for segment in mock_transcript_segments
    ]

    test_transcript = ChapteredTranscript(
        url="https://example.com/video",
        webpage_url_domain="example.com",
        video_id="video",
        title="Test Video Title",
        language="en",
        chaptered_at_source=True,
        chapters=[
            TranscriptChapter(
                title="Chapter 1",
                segments=segments_dicts,
            ),
        ],
    )

    # Act
    formatted_output = formatter.format_chaptered_transcript(
        chaptered_transcript=test_transcript
    )

    # Assert
    assert formatted_output.title == "Test Video Title"
    assert "# Test Video Title" in formatted_output.transcript
    assert "https://example.com/video" in formatted_output.transcript
    assert "## Chapter 1" in formatted_output.transcript
    assert (
        "Hi class. So today I'll be talking about climate change"
        in formatted_output.transcript
    )
    assert formatted_output.transcript.count("\n\n") > 6
    assert "(0:00:00)" not in formatted_output.transcript


def test_markdown_formatter_with_segmentation(
    mock_transcript_segments: typing.List[Segment], mock_llm_adapter: LLMAdapter
) -> None:
    # Arrange
    def mocked_get_topic_change(
        paragraphs: typing.List[typing.List[str]],
    ) -> typing.List[int]:
        if len(paragraphs) == 1:
            return []
        return [1]

    mock_llm_adapter.get_topic_changing_paragraph_indexes.side_effect = (  # type: ignore
        mocked_get_topic_change
    )

    def mock_generate_title_for_paragraphs(
        paragraphs: typing.List[typing.List[str]],
    ) -> str:
        return "Chapter Title"

    mock_llm_adapter.generate_title_for_paragraphs.side_effect = (  # type: ignore
        mock_generate_title_for_paragraphs
    )

    sat = SaT("sat-3l")
    paragraphs_segmenter = ParagraphsSegmenter(sat=sat)
    segmenter = LLMTopicSegmenter(llm_adapter=mock_llm_adapter)
    formatter = MarkdownFormatter(
        paragraphs_segmenter=paragraphs_segmenter,
        to_timestamp_paragraphs=False,
        topic_segmenter=segmenter,
    )

    segments_dicts = [
        {
            "start_second": segment.start_second,
            "end_second": segment.end_second,
            "text": segment.text,
        }
        for segment in mock_transcript_segments
    ]

    test_transcript = ChapteredTranscript(
        url="https://example.com/video",
        title="Test Video Title",
        webpage_url_domain="example.com",
        video_id="video",
        language="en",
        chaptered_at_source=False,
        chapters=[
            TranscriptChapter(
                title="Untitled Chapter",
                segments=segments_dicts,
            ),
        ],
    )

    # Act
    formatted_output = formatter.format_chaptered_transcript(
        chaptered_transcript=test_transcript
    )

    # Assert
    assert "# Test Video Title" in formatted_output.transcript
    assert "## Chapter Title" in formatted_output.transcript
    assert formatted_output.transcript.count("\n\n") > 6
    assert "(0:00:00)" not in formatted_output.transcript


def test_format_chaptered_transcript_timestamp_paragraphs(
    mock_transcript_segments: typing.List[Segment],
) -> None:
    # Arrange
    sat = SaT("sat-3l")
    paragraphs_segmenter = ParagraphsSegmenter(sat=sat)
    formatter = MarkdownFormatter(
        paragraphs_segmenter=paragraphs_segmenter, to_timestamp_paragraphs=True
    )

    segments_dicts = [
        {
            "start_second": segment.start_second,
            "end_second": segment.end_second,
            "text": segment.text,
        }
        for segment in mock_transcript_segments
    ]

    test_transcript = ChapteredTranscript(
        url="https://example.com/video",
        webpage_url_domain="example.com",
        video_id="video",
        title="Test Video Title",
        language="en",
        chaptered_at_source=True,
        chapters=[
            TranscriptChapter(
                title="Chapter 1",
                segments=segments_dicts,
            ),
        ],
    )

    # Act
    formatted_output = formatter.format_chaptered_transcript(
        chaptered_transcript=test_transcript
    )

    # Assert
    assert formatted_output.title == "Test Video Title"
    assert "(0:00:00)" in formatted_output.transcript
