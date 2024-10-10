import typing

from pydantic import BaseModel

from yt2doc.extraction import interfaces as extraction_interfaces


class Chapter(BaseModel):
    title: str
    text: str


class FormattedTranscript(BaseModel):
    title: str
    transcript: str


class FormattedPlaylist(BaseModel):
    title: str
    transcripts: typing.Sequence[FormattedTranscript]


class ITopicSegmenter(typing.Protocol):
    def segment(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> typing.Sequence[Chapter]: ...


class IFormatter(typing.Protocol):
    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> FormattedTranscript: ...

    def format_chaptered_playlist_transcripts(
        self, chaptered_playlist: extraction_interfaces.ChapteredTranscribedPlaylist
    ) -> FormattedPlaylist: ...
