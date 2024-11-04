import typing
import logging

from tqdm import tqdm

from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class LLMTopicSegmenter:
    def __init__(self, llm_adapter: interfaces.ILLMAdapter) -> None:
        self.llm_adapter = llm_adapter

    def segment(
        self,
        sentences_in_paragraphs: typing.List[typing.List[interfaces.Sentence]],
    ) -> typing.Sequence[interfaces.Chapter]:
        group_size = 8
        grouped_paragraphs_with_overlap = [
            (i, sentences_in_paragraphs[i : i + group_size])
            for i in range(0, len(sentences_in_paragraphs), group_size - 1)
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
            truncated_group_paragraphs_texts = [
                [sentence.text for sentence in paragraph]
                for paragraph in truncated_group_paragraphs
            ]

            paragraph_indexes = self.llm_adapter.get_topic_changing_paragraph_indexes(
                paragraphs=truncated_group_paragraphs_texts,
            )

            logger.info(f"paragraph indexes from LLM: {paragraph_indexes}")
            aligned_indexes = [
                start_index + index for index in sorted(paragraph_indexes)
            ]
            topic_changed_indexes += aligned_indexes

        if len(topic_changed_indexes) == 0:
            truncated_paragraphs_in_chapter = [p[:10] for p in sentences_in_paragraphs]
            truncated_paragraphs_texts = [
                [sentence.text for sentence in paragraph]
                for paragraph in truncated_paragraphs_in_chapter
            ]
            title = self.llm_adapter.generate_title_for_paragraphs(
                paragraphs=truncated_paragraphs_texts
            )
            return [
                interfaces.Chapter(
                    title=title,
                    paragraphs=sentences_in_paragraphs,
                )
            ]

        paragraphs_in_chapters: typing.List[
            typing.List[typing.List[interfaces.Sentence]]
        ] = []
        current_chapter_paragraphs: typing.List[typing.List[interfaces.Sentence]] = []
        for index, sentences_in_paragraph in enumerate(sentences_in_paragraphs):
            if index in topic_changed_indexes:
                paragraphs_in_chapters.append(current_chapter_paragraphs)
                current_chapter_paragraphs = []
            current_chapter_paragraphs.append(sentences_in_paragraph)
        paragraphs_in_chapters.append(current_chapter_paragraphs)

        chapters: typing.List[interfaces.Chapter] = []
        for paragraphs_in_chapter in tqdm(
            paragraphs_in_chapters, desc="Generating titles for chapters"
        ):
            truncated_paragraphs_in_chapter = [p[:10] for p in paragraphs_in_chapter]
            truncated_paragraphs_texts = [
                [sentence.text for sentence in paragraph]
                for paragraph in truncated_paragraphs_in_chapter
            ]
            title = self.llm_adapter.generate_title_for_paragraphs(
                paragraphs=truncated_paragraphs_texts
            )
            chapters.append(
                interfaces.Chapter(title=title, paragraphs=paragraphs_in_chapter)
            )

        return chapters
