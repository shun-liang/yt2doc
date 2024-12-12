import typing
from pathlib import Path

import instructor

from wtpsplit import SaT
from openai import OpenAI

from yt2doc.media.media_info_extractor import YtDLPMediaInfoExtractor
from yt2doc.transcription.transcriber import Transcriber
from yt2doc.transcription import interfaces as transcription_interfaces
from yt2doc.extraction.file_cache import FileCache
from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.extraction.extractor import Extractor
from yt2doc.formatting.formatter import MarkdownFormatter
from yt2doc.formatting.llm_topic_segmenter import LLMTopicSegmenter
from yt2doc.formatting.llm_adapter import LLMAdapter
from yt2doc.formatting.paragraphs_segmenter import ParagraphsSegmenter
from yt2doc.yt2doc import Yt2Doc


DEFAULT_CACHE_PATH = Path.home() / ".yt2doc"


class LLMModelNotSpecified(Exception):
    pass


def get_yt2doc(
    whisper_adapter: transcription_interfaces.IWhisperAdapter,
    meta: extraction_interfaces.MetaDict,
    sat_model: str,
    segment_unchaptered: bool,
    ignore_source_chapters: bool,
    to_timestamp_paragraphs: bool,
    add_table_of_contents: bool,
    llm_model: typing.Optional[str],
    llm_server: str,
    llm_api_key: str,
    temp_dir: Path,
    yt_dlp_options: typing.Dict[str, typing.Any],
) -> Yt2Doc:
    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)
    file_cache = FileCache(
        cache_dir=DEFAULT_CACHE_PATH,
        meta=meta,
    )

    sat = SaT(sat_model)
    paragraphs_segmenter = ParagraphsSegmenter(sat=sat)
    if segment_unchaptered is True:
        if llm_model is None:
            raise LLMModelNotSpecified(
                "segment_unchaptered is set to True but llm_model is not specified."
            )
        llm_client = instructor.from_openai(
            OpenAI(
                base_url=llm_server,
                api_key=llm_api_key,
            ),
            mode=instructor.Mode.JSON,
        )
        llm_adapter = LLMAdapter(llm_client=llm_client, llm_model=llm_model)
        llm_topic_segmenter = LLMTopicSegmenter(llm_adapter=llm_adapter)
        formatter = MarkdownFormatter(
            paragraphs_segmenter=paragraphs_segmenter,
            to_timestamp_paragraphs=to_timestamp_paragraphs,
            add_table_of_contents=add_table_of_contents,
            topic_segmenter=llm_topic_segmenter,
        )
    else:
        formatter = MarkdownFormatter(
            paragraphs_segmenter=paragraphs_segmenter,
            to_timestamp_paragraphs=to_timestamp_paragraphs,
            add_table_of_contents=add_table_of_contents,
        )

    media_info_extractor = YtDLPMediaInfoExtractor(
        temp_dir=temp_dir,
        extra_opts=yt_dlp_options or {},
    )
    transcriber = Transcriber(
        temp_dir=temp_dir,
        whisper_adapter=whisper_adapter,
    )
    extractor = Extractor(
        media_info_extractor=media_info_extractor,
        transcriber=transcriber,
        file_cache=file_cache,
        ignore_source_chapters=ignore_source_chapters,
    )

    yt2doc = Yt2Doc(extractor=extractor, formatter=formatter)
    return yt2doc
