import typing

from pydantic import BaseModel

from yt2doc.extraction import interfaces as extraction_interfaces


class FormattedTranscript(BaseModel):
    title: str
    transcript: str


class FormattedPlaylist(BaseModel):
    title: str
    transcripts: typing.Sequence[FormattedTranscript]


class IFormatter(typing.Protocol):
    def format_chaptered_transcript(
        self, chaptered_transcript: extraction_interfaces.ChapteredTranscript
    ) -> FormattedTranscript: ...

    def format_chaptered_playlist_transcripts(
        self, chaptered_playlist: extraction_interfaces.ChapteredTranscribedPlaylist
    ) -> FormattedPlaylist: ...
