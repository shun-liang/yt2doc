import typing

from pydantic import BaseModel

from yt2doc.transcription import interfaces as transcription_interfaces


class TranscriptChapter(BaseModel):
    title: str
    segments: typing.Sequence[transcription_interfaces.Segment]


class ChapteredTranscript(BaseModel):
    url: str
    title: str
    video_id: str
    webpage_url_domain: str
    language: str
    chapters: typing.Sequence[TranscriptChapter]
    chaptered_at_source: bool


class ChapteredTranscribedPlaylist(BaseModel):
    url: str
    title: str
    transcripts: typing.Sequence[ChapteredTranscript]


MetaDict = typing.Dict[str, typing.Union[str, int, float]]


class IFileCache(typing.Protocol):
    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[ChapteredTranscript]: ...
    def cache_chaptered_transcript(
        self,
        video_id: str,
        transcript: ChapteredTranscript,
    ) -> None: ...


class IExtractor(typing.Protocol):
    def extract_by_chapter(
        self,
        video_url: str,
        skip_cache: bool,
    ) -> ChapteredTranscript: ...

    def extract_playlist_by_chapter(
        self, playlist_url: str, skip_cache: bool
    ) -> ChapteredTranscribedPlaylist: ...
