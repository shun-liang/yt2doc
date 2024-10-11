import typing
from pathlib import Path

import instructor

from wtpsplit import SaT
from openai import OpenAI

from yt2doc.youtube.yt_video_info_extractor import YtVideoInfoExtractor
from yt2doc.transcription.transcriber import Transcriber
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction.file_cache import FileCache
from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.extraction.extractor import Extractor
from yt2doc.formatting.formatter import MarkdownFormatter
from yt2doc.formatting.llm_topic_segmenter import LLMTopicSegmenter
from yt2doc.yt2doc import Yt2Doc


DEFAULT_CACHE_PATH = Path.home() / ".yt2doc"


class LLMModelNotSpecified(Exception):
    pass


def get_yt2doc(
    whisper_adapter: transcription_interfaces.IWhisperAdapter,
    meta: extraction_interfaces.MetaDict,
    sat_model: str,
    segment_unchaptered: bool,
    llm_model: typing.Optional[str],
    temp_dir: Path,
) -> Yt2Doc:
    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)
    file_cache = FileCache(
        cache_dir=DEFAULT_CACHE_PATH,
        meta=meta,
    )

    sat = SaT(sat_model)
    if segment_unchaptered is True:
        if llm_model is None:
            raise LLMModelNotSpecified(
                "segment_unchaptered is set to True but llm_model is not specified."
            )
        llm_client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama",  # required, but unused
            ),
            mode=instructor.Mode.JSON,
        )

        llm_topic_segmenter = LLMTopicSegmenter(llm_client=llm_client, model=llm_model)
        formatter = MarkdownFormatter(sat=sat, topic_segmenter=llm_topic_segmenter)
    else:
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
