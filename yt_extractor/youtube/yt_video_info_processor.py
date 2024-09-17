import typing

import instructor

from textwrap import dedent

from openai import OpenAI
from pydantic import BaseModel

from yt_extractor.youtube import interfaces


class CleanedYtVideoDescription(BaseModel):
    cleaned_description: str


class YtVideoInfoProcessor:
    def __init__(self, llm_client: OpenAI, llm_model: str) -> None:
        self.instructor_client = instructor.from_openai(
            llm_client,
            mode=instructor.Mode.JSON,
        )
        self.llm_model = llm_model

    def _clean_video_description(self, title: str, video_description: str) -> str:
        resp = self.instructor_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": dedent("""
                        You are a robust editor that cleans up the description of YouTube video.
                        The input contains the TITLE of the video, so that you are informed about the video's topic,
                        and the DESCRIPTION of the video, which you need to clean up.
                        Remove any sponsored content, URL, hash tag, emoji, or timestamps.
                        Output the cleaned description.
                    """),
                },
                {
                    "role": "user",
                    "content": dedent(f"""
                        TITLE: 
                        {title},

                        DESCRIPTION:
                        {video_description}
                    """),
                },
            ],
            response_model=CleanedYtVideoDescription,
        )
        return resp.cleaned_description

    def _get_speakers(
        self, title: str, cleaned_video_description: str
    ) -> typing.Sequence[interfaces.Speaker]:
        resp = self.instructor_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": dedent("""
                        You are a YouTube information extracting assistant.
                        You will be given the TITLE and the DESCRIPTION of the video.
                        If from the description you find any speakers of the video,
                        return their names and their roles in the video.
                        If not, or if you are not confident, just return an empty list.
                    """),
                },
                {
                    "role": "user",
                    "content": dedent(f"""
                        TITLE: 
                        {title},

                        DESCRIPTION:
                        {cleaned_video_description}
                    """),
                },
            ],
            response_model=typing.List[interfaces.Speaker],
        )
        return resp

    def process_video_info(
        self, title: str, video_description: str
    ) -> interfaces.ProcessedInfo:
        cleaned_video_description = self._clean_video_description(
            title=title, video_description=video_description
        )
        speakers = self._get_speakers(
            title=title, cleaned_video_description=cleaned_video_description
        )
        return interfaces.ProcessedInfo(
            cleaned_description=cleaned_video_description, speakers=speakers
        )
