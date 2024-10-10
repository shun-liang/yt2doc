import typing
import json
import hashlib
import logging

from pathlib import Path

from pydantic import ValidationError

from yt2doc.extraction import interfaces

logger = logging.getLogger(__file__)


class FileCache:
    def __init__(self, cache_dir: Path, meta: interfaces.MetaDict) -> None:
        self.cache_dir = cache_dir
        self.meta = meta
        self.hashed_meta = hashlib.md5(
            json.dumps(meta, sort_keys=True).encode()
        ).hexdigest()

    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[typing.Sequence[interfaces.TranscriptChapter]]:
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
        try:
            return [
                interfaces.TranscriptChapter(**chapter) for chapter in chapter_dicts
            ]
        except ValidationError as e:
            logger.warning(f"Validation error while trying to read from cache: {e}")
            return None

    def cache_chaptered_transcript(
        self,
        video_id: str,
        chapters: typing.Sequence[interfaces.TranscriptChapter],
    ) -> None:
        dir = self.cache_dir / video_id / "chaptered_transcript"
        dir.mkdir(exist_ok=True, parents=True)
        file_path = dir / f"{self.hashed_meta}.json"

        with open(file_path, "w+") as f:
            json.dump(
                {
                    "chapters": [chapter.model_dump() for chapter in chapters],
                    "meta": self.meta,
                },
                f,
            )
