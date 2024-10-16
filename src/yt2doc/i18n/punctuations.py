import typing

from pydantic import BaseModel


class Punctuations(BaseModel):
    full_stop: str
    comma: str
    question_mark: str
    exclamation_mark: str
    white_space: str


PUNCTUATIONS_IN_LANGUAGES: typing.Dict[str, Punctuations] = {
    "en": Punctuations(
        full_stop=".",
        comma=", ",
        question_mark="?",
        exclamation_mark="!",
        white_space=" ",
    ),
    "zh": Punctuations(
        full_stop="。",
        comma="，",
        question_mark="？",
        exclamation_mark="！",
        white_space="",
    ),
    "jp": Punctuations(
        full_stop="。",
        comma="、",
        question_mark="？",
        exclamation_mark="！",
        white_space="",
    ),
}


def get_punctuations(language_code: str) -> Punctuations:
    if language_code not in PUNCTUATIONS_IN_LANGUAGES.keys():
        return PUNCTUATIONS_IN_LANGUAGES["en"]
    return PUNCTUATIONS_IN_LANGUAGES[language_code]
