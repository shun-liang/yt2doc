import io
import logging
import re
import subprocess
import typing

from pathlib import Path

from yt2doc.transcription import interfaces


logger = logging.getLogger(__file__)


class CannotParseWhisperCppLineException(Exception):
    pass


class WhisperCppReturnNonZero(Exception):
    pass


class CannotDetectLanguage(Exception):
    pass


# TODO: Implement this properly once there is a Python binding of whisper.cpp
# that treat CUDA and Apple Silicon / MPS as first class citizen
# and does not require installing from source with special compiler flags
# (e.g. [pywhispercpp](https://github.com/abdeladim-s/pywhispercpp)).
class WhisperCppAdapter:
    def __init__(self, whisper_cpp_executable: Path, whisper_cpp_model: Path) -> None:
        self.whisper_cpp_executable = whisper_cpp_executable
        self.whisper_cpp_model = whisper_cpp_model

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        h, m, s = time_str.split(":")
        seconds = int(h) * 3600 + int(m) * 60 + float(s)
        return round(seconds, 2)

    def _parse_whisper_line(self, line: str) -> interfaces.Segment:
        pattern = (
            r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s{2}(.*)"
        )
        match = re.match(pattern, line)
        if match:
            start_time, end_time, text = match.groups()
            return interfaces.Segment(
                start=self._time_to_seconds(start_time),
                end=self._time_to_seconds(end_time),
                text=text,
            )
        raise CannotParseWhisperCppLineException(
            f'Cannot parse whisper.cpp line: "{line}"'
        )

    def detect_language(self, audio_path: Path) -> str:
        result = subprocess.Popen(
            [
                self.whisper_cpp_executable,
                "-m",
                self.whisper_cpp_model,
                "-f",
                audio_path,
                "--detect-language",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        stderr = result.stderr
        if stderr is None:
            raise CannotDetectLanguage("stderr")

        language_code_lines = [
            line
            for line in stderr
            if line.startswith("whisper_full_with_state: auto-detected language")
        ]
        if len(language_code_lines) != 1:
            raise CannotDetectLanguage(
                f"Length of line containing language code in stderr is {len(language_code_lines)}"
            )

        language_code_line = language_code_lines[0]
        pattern = r"whisper_full_with_state: auto-detected language: ([a-z]{2})"
        match = re.search(pattern, language_code_line)
        if match is None:
            raise CannotDetectLanguage(
                f"Unexpected matched language code line: {language_code_line}"
            )
        matched = match.group(1)
        return str(matched)  # typing: ignore

    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[interfaces.Segment]:
        proc = subprocess.Popen(
            [
                self.whisper_cpp_executable,
                "-m",
                self.whisper_cpp_model,
                "-f",
                audio_path,
                "--prompt",
                initial_prompt,
            ],
            stdout=subprocess.PIPE,
            bufsize=1,
        )

        stdout = proc.stdout
        if stdout is None:
            raise CannotParseWhisperCppLineException("stdout is None.")
        for line in stdout:
            try:
                decoded_line = line.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    decoded_line = line.decode("latin-1")
                except UnicodeDecodeError:
                    logger.warning(f"Couldn't decode line: {line!r}")
                continue

            if decoded_line in ["", "\n"]:
                continue
            yield self._parse_whisper_line(decoded_line)

        output, error = proc.communicate()
        if proc.returncode != 0:
            raise WhisperCppReturnNonZero(
                f'whisper.cpp command returned errored. output: "{output!r}", error: "{error!r}"'
            )

        logger.info(error)
