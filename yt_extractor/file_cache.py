import typing
import json
import hashlib

from dataclasses import dataclass
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
    def __init__(self, cache_dir: Path, meta: MetaDict) -> None:
        self.cache_dir = cache_dir
        self.meta = meta
        self.hashed_meta = hashlib.md5(
            json.dumps(meta, sort_keys=True).encode()
        ).hexdigest()

    def get_transcript(self, video_id: str) -> typing.Optional[str]:
        file_path = (
            self.cache_dir / video_id / "transcript" / f"{self.hashed_meta}.json"
        )
        if not (file_path.exists()):
            return None

        with open(file_path, "r") as f:
            transcript_dict = json.load(f)

        return transcript_dict["transcript"]  # type: ignore

    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[typing.Sequence[TranscriptChapter]]:
        file_path = (
            self.cache_dir
            / video_id
            / "chaptered_transcript"
            / f"{self.hashed_meta}.json"
        )
        if not (file_path.exists()):
            return None

        with open(file_path, "r") as f:
            chaptered_transcript_dict = json.load(f)

        chapter_dicts: typing.List[typing.Dict[str, typing.Any]] = (
            chaptered_transcript_dict["chapters"]
        )
        return [TranscriptChapter(**chapter) for chapter in chapter_dicts]

    def cache_transcript(self, video_id: str, transcript: str) -> None:
        dir = self.cache_dir / video_id / "transcript"
        dir.mkdir(exist_ok=True, parents=True)
        file_path = dir / f"{self.hashed_meta}.json"

        with open(file_path, "w+") as f:
            json.dump(
                {
                    "transcript": transcript,
                    "meta": self.meta,
                },
                f,
            )

    def cache_chaptered_transcript(
        self,
        video_id: str,
        chapters: typing.Sequence[TranscriptChapterLike],
    ) -> None:
        dir = self.cache_dir / video_id / "chaptered_transcript"
        dir.mkdir(exist_ok=True, parents=True)
        file_path = dir / f"{self.hashed_meta}.json"

        with open(file_path, "w+") as f:
            json.dump(
                {
                    "chapters": [
                        {"title": chapter.title, "text": chapter.text}
                        for chapter in chapters
                    ],
                    "meta": self.meta,
                },
                f,
            )
