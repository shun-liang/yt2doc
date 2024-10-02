import typing

from pathlib import Path

from wtpsplit import SaT

from yt2doc.youtube.yt_video_info_extractor import YtVideoInfoExtractor
from yt2doc.transcription.transcriber import Transcriber
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction.file_cache import FileCache
from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.extraction.extractor import Extractor
from yt2doc.formatting.formatter import MarkdownFormatter
from yt2doc.yt2doc import Yt2Doc


DEFAULT_CACHE_PATH = Path.home() / ".yt-extractor"


def get_yt2doc(
    whisper_adapter: transcription_interfaces.IWhisperAdapter,
    meta: extraction_interfaces.MetaDict,
    sat_model: str,
    temp_dir: Path,
) -> Yt2Doc:
    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)
    file_cache = FileCache(
        cache_dir=DEFAULT_CACHE_PATH,
        meta=meta,
    )

    sat = SaT(sat_model)
    formatter = MarkdownFormatter(sat=sat)

    video_info_extractor = YtVideoInfoExtractor(temp_dir=temp_dir)
    transcriber = Transcriber(
        temp_dir=temp_dir,
        whisper_adapter=whisper_adapter,
    )
    extractor = Extractor(
        video_info_extractor=video_info_extractor,
        transcriber=transcriber,
        file_cache=file_cache,
    )

    yt2doc = Yt2Doc(extractor=extractor, formatter=formatter)
    return yt2doc
