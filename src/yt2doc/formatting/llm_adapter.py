import typing

from instructor import Instructor
from pydantic import BaseModel, AfterValidator


class LLMAdapter:
    def __init__(self, llm_client: Instructor, llm_model: str) -> None:
        self.llm_client = llm_client
        self.llm_model = llm_model

    def get_topic_changing_paragraph_indexes(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> typing.Sequence[int]:
        def validate_paragraph_indexes(v: typing.List[int]) -> typing.List[int]:
            n = len(paragraphs)
            unique_values = set(v)
            if len(unique_values) != len(v):
                raise ValueError("All elements must be unique")
            for i in v:
                if i <= 0:
                    raise ValueError(
                        f"All elements must be greater than 0 and less than {n}. Paragraph index {i} is less than or equal to 0"
                    )
                if i >= n:
                    raise ValueError(
                        f"All elements must be greater than 0 and less than {n}. Paragraph index {i} is greater or equal to {n}"
                    )

            return v

        paragraph_texts = ["\n\n".join(p) for p in paragraphs]

        class Result(BaseModel):
            paragraph_indexes: typing.Annotated[
                typing.List[int], AfterValidator(validate_paragraph_indexes)
            ]

        result = self.llm_client.chat.completions.create(
            model=self.llm_model,
            response_model=Result,
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are a smart assistant who reads paragraphs of text from an audio transcript and
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
                        <paragraph {{ loop.index0 }}>
                        {{ paragraph }}
                        </ paragraph {{ loop.index0 }}>
                        {% endfor %}
                    """,
                },
            ],
            context={
                "paragraphs": paragraph_texts,
            },
        )
        return result.paragraph_indexes

    def generate_title_for_paragraphs(
        self, paragraphs: typing.List[typing.List[str]]
    ) -> str:
        text = "\n\n".join(["".join(p) for p in paragraphs])
        title = self.llm_client.chat.completions.create(
            model=self.llm_model,
            response_model=str,
            messages=[
                {
                    "role": "system",
                    "content": """
                        Please generate a short title for the following text.

                        Be VERY SUCCINCT. No more than 6 words.
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
