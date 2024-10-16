import typing
import json
import hashlib
import logging

from pathlib import Path

from pydantic import BaseModel, ValidationError

from yt2doc.extraction import interfaces

logger = logging.getLogger(__file__)


class CachedTranscript(BaseModel):
    transcript: interfaces.ChapteredTranscript
    meta: interfaces.MetaDict


class FileCache:
    def __init__(self, cache_dir: Path, meta: interfaces.MetaDict) -> None:
        self.cache_dir = cache_dir
        self.meta = meta
        self.hashed_meta = hashlib.md5(
            json.dumps(meta, sort_keys=True).encode()
        ).hexdigest()

    def get_chaptered_transcript(
        self, video_id: str
    ) -> typing.Optional[interfaces.ChapteredTranscript]:
        file_path = (
            self.cache_dir
            / video_id
            / "chaptered_transcript"
            / f"{self.hashed_meta}.json"
        )
        if not (file_path.exists()):
            return None

        with open(file_path, "r") as f:
            cached_transcript_dict = json.load(f)

        try:
            cached_transcript = CachedTranscript(**cached_transcript_dict)
        except ValidationError as e:
            logger.warning(f"Validation error while trying to read from cache: {e}")
            return None

        return cached_transcript.transcript

    def cache_chaptered_transcript(
        self, video_id: str, transcript: interfaces.ChapteredTranscript
    ) -> None:
        dir = self.cache_dir / video_id / "chaptered_transcript"
        dir.mkdir(exist_ok=True, parents=True)
        file_path = dir / f"{self.hashed_meta}.json"
        transcript_to_cache = CachedTranscript(transcript=transcript, meta=self.meta)

        with open(file_path, "w+") as f:
            serialized = transcript_to_cache.model_dump()
            json.dump(serialized, f)
