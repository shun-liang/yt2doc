import typing

from pydantic import BaseModel

from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.transcription import interfaces as transcription_interfaces


class Sentence(BaseModel):
    start_second: float
    text: str


class Chapter(BaseModel):
    title: str
    paragraphs: typing.Sequence[typing.Sequence[Sentence]]


class FormattedTranscript(BaseModel):
    title: str
    transcript: str


class FormattedPlaylist(BaseModel):
    title: str
    transcripts: typing.Sequence[FormattedTranscript]


class IParagraphsSegmenter(typing.Protocol):
    def segment(
        self, transcription_segments: typing.Sequence[transcription_interfaces.Segment]
    ) -> typing.List[typing.List[Sentence]]: ...


class ILLMAdapter(typing.Protocol):
    def get_topic_changing_paragraph_indexes(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> typing.Sequence[int]: ...

    def generate_title_for_paragraphs(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> str: ...


class ITopicSegmenter(typing.Protocol):
    def segment(
        self, sentences_in_paragraphs: typing.List[typing.List[Sentence]]
    ) -> typing.Sequence[Chapter]: ...


class IFormatter(typing.Protocol):
    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> FormattedTranscript: ...

    def format_chaptered_playlist_transcripts(
        self, chaptered_playlist: extraction_interfaces.ChapteredTranscribedPlaylist
    ) -> FormattedPlaylist: ...
