import typing
import logging

from tqdm import tqdm

from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class LLMTopicSegmenter:
    def __init__(self, llm_adapter: interfaces.ILLMAdapter) -> None:
        self.llm_adapter = llm_adapter

    def _get_title_for_chapter(self, paragraphs: typing.List[typing.List[str]]) -> str:
        truncated_paragraphs = [p[:10] for p in paragraphs]
        return self.llm_adapter.generate_title_for_paragraphs(
            paragraphs=truncated_paragraphs
        )

    def segment(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> typing.Sequence[interfaces.Chapter]:
        group_size = 8
        grouped_paragraphs_with_overlap = [
            (i, paragraphs[i : i + group_size])
            for i in range(0, len(paragraphs), group_size - 1)
        ]
        logger.info(
            f"grouped_paragraphs_with_overlap: {grouped_paragraphs_with_overlap}"
        )
        topic_changed_indexes = []
        for start_index, grouped_paragraphs in tqdm(
            grouped_paragraphs_with_overlap, desc="Finding topic change points"
        ):
            truncate_sentence_index = 6
            truncated_group_paragraphs = [
                paragraph[:truncate_sentence_index] for paragraph in grouped_paragraphs
            ]

            paragraph_indexes = self.llm_adapter.get_topic_changing_paragraph_indexes(
                paragraphs=truncated_group_paragraphs
            )

            logger.info(f"paragraph indexes from LLM: {paragraph_indexes}")
            aligned_indexes = [
                start_index + index for index in sorted(paragraph_indexes)
            ]
            topic_changed_indexes += aligned_indexes

        if len(topic_changed_indexes) == 0:
            paragraph_texts = ["".join(paragraph) for paragraph in paragraphs]
            text = "\n\n".join(paragraph_texts)
            return [
                interfaces.Chapter(
                    title=self._get_title_for_chapter(paragraphs=paragraphs),
                    text=text,
                )
            ]

        chapter_paragraphs: typing.List[typing.List[typing.List[str]]] = []
        current_chapter_paragraphs: typing.List[typing.List[str]] = []
        for index, paragraph in enumerate(paragraphs):
            if index in topic_changed_indexes:
                chapter_paragraphs.append(current_chapter_paragraphs)
                current_chapter_paragraphs = []
            current_chapter_paragraphs.append(paragraph)
        chapter_paragraphs.append(current_chapter_paragraphs)

        chapter_titles_and_texts: typing.List[typing.Tuple[str, str]] = []
        for chapter in tqdm(chapter_paragraphs, desc="Generating titles for chapters"):
            paragraphs_: typing.List[str] = []
            for paragraph in chapter:
                paragraph_text = "".join(paragraph)
                paragraphs_.append(paragraph_text)
            title = self._get_title_for_chapter(paragraphs=chapter)
            chapter_titles_and_texts.append((title, "\n\n".join(paragraphs_)))
        chapters = [
            interfaces.Chapter(title=title, text=text)
            for title, text in chapter_titles_and_texts
        ]
        return chapters
