import typing
import logging

import instructor

from yt2doc.formatting import interfaces

logger = logging.getLogger(__file__)


class LLMTopicSegmenter:
    def __init__(self, llm_client: instructor.Instructor, model: str) -> None:
        self.llm_client = llm_client
        self.model = model

    def _get_title_for_chapter(self, text: str) -> str:
        title = self.llm_client.chat.completions.create(
            model=self.model,
            response_model=str,
            messages=[
                {
                    "role": "system",
                    "content": """
                        Please generate a short title for the following text.

                        Be very succinct. No more than 6 words.
                    """,
                },
                {
                    "role": "user",
                    "content": """
                        {{ text }}
                    """,
                },
            ],
            context={
                "text": text,
            },
        )
        return title

    def segment(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> typing.Sequence[interfaces.Chapter]:
        group_size = 6
        grouped_paragraphs_with_overlap = [
            (i, paragraphs[i : i + group_size])
            for i in range(0, len(paragraphs), group_size - 1)
        ]
        logger.info(
            f"grouped_paragraphs_with_overlap: {grouped_paragraphs_with_overlap}"
        )
        topic_changed_indexes = []
        for start_index, grouped_paragraphs in grouped_paragraphs_with_overlap:

            truncated_grouped_paragraph_texts = [
                "".join(paragraph[:6]) for paragraph in grouped_paragraphs
            ]
            result = self.llm_client.chat.completions.create(
                model=self.model,
                response_model=typing.List[int],
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are an smart assistant who reads paragraphs of text from an audio transcript and
                            find the paragraphs that significantly change topic from the previous paragraph.

                            Make sure only mark paragraphs that talks about a VERY DIFFERENT topic from the previous one.

                            The response should be an array of the index number of such paragraphs, such as `[1, 3, 5]`

                            If there is no paragraph that changes topic, then return an empty list.
                            """,
                    },
                    {
                        "role": "user",
                        "content": """
                            {% for paragraph in paragraphs %}
                            <paragraph {{ loop.index }}>
                            {{ paragraph }}
                            </ paragraph {{ loop.index }}>
                            {% endfor %}
                        """,
                    },
                ],
                context={
                    "paragraphs": truncated_grouped_paragraph_texts,
                },
            )
            logger.info(f"paragraph indexes from LLM: {result}")
            aligned_indexes = [start_index + index for index in result]
            topic_changed_indexes += aligned_indexes

        if len(topic_changed_indexes) == 0:
            paragraph_texts = ["".join(paragraph) for paragraph in paragraphs]
            text = "\n\n".join(paragraph_texts)
            return [
                interfaces.Chapter(
                    title=self._get_title_for_chapter(text=text),
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
        # logger.info(chapter_paragraphs)
        chapter_texts: typing.List[str] = []
        for chapter in chapter_paragraphs:
            chapter_text = ""
            for paragraph in chapter:
                paragraph_text = "".join(paragraph)
                chapter_text = "\n\n".join([chapter_text, paragraph_text])
            chapter_texts.append(chapter_text)
        chapters = [
            interfaces.Chapter(
                title=self._get_title_for_chapter(text=text), text=text.strip()
            )
            for text in chapter_texts
        ]
        return chapters
