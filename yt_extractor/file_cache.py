import typing
import json

from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path


class TranscriptChapterLike(typing.Protocol):
    title: str
    text: str


@dataclass
class TranscriptChapter:
    title: str
    text: str


MetaDict = typing.Dict[str, typing.Union[str, int, float]]


class FileCache:
    transcript_file_name = "transcript.json"
    chaptered_transcript_file_name = "chaptered_transcript.json"

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir

    def get_transcript(self, video_id: str) -> typing.Optional[str]:
        file_path = self.cache_dir / video_id / self.transcript_file_name
        if not (file_path.exists()):
            return None

        with open(file_path, "r") as f:
            transcript_dict = json.load(f)

        return transcript_dict["transcript"]  # type: ignore

    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[typing.Sequence[TranscriptChapter]]:
        file_path = self.cache_dir / video_id / self.chaptered_transcript_file_name
        if not (file_path.exists()):
            return None

        with open(file_path, "r") as f:
            chaptered_transcript_dict = json.load(f)

        chapter_dicts: typing.List[typing.Dict[str, typing.Any]] = (
            chaptered_transcript_dict["chapters"]
        )
        return [TranscriptChapter(**chapter) for chapter in chapter_dicts]

    def cache_transcript(self, video_id: str, transcript: str, meta: MetaDict) -> None:
        dir = self.cache_dir / video_id
        dir.mkdir(exist_ok=True)
        file_path = dir / self.transcript_file_name
        with open(file_path, "w+") as f:
            json.dump(
                {
                    "transcript": transcript,
                    "meta": {**meta, "timestamp": datetime.now(UTC).isoformat()},
                },
                f,
            )

    def cache_chaptered_transcript(
        self,
        video_id: str,
        chapters: typing.Sequence[TranscriptChapterLike],
        meta: MetaDict,
    ) -> None:
        dir = self.cache_dir / video_id
        dir.mkdir(exist_ok=True)
        file_path = dir / self.chaptered_transcript_file_name
        with open(file_path, "w+") as f:
            json.dump(
                {
                    "chapters": [
                        {"title": chapter.title, "text": chapter.text}
                        for chapter in chapters
                    ],
                    "meta": {**meta, "timestamp": datetime.now(UTC).isoformat()},
                },
                f,
            )
