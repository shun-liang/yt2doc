import logging
import re
import subprocess
import typing

import ffmpeg

from pathlib import Path

from yt_extractor.transcription import interfaces


logger = logging.getLogger(__file__)


class CannotParseWhisperCppLineException(Exception):
    pass


class WhisperCppReturnNonZero(Exception):
    pass


class WhisperCppAdapter:
    def __init__(self, whisper_cpp_executable: Path, whisper_cpp_model: Path) -> None:
        self.whisper_cpp_executable = whisper_cpp_executable
        self.whisper_cpp_model = whisper_cpp_model

    @staticmethod
    def _convert_audio_to_wav(audio_path: Path) -> Path:
        audio_format: str = ffmpeg.probe(audio_path)["format"]["format_name"]
        if audio_format == "wav":
            return audio_path

        wav_audio_path = audio_path.with_suffix(".wav")
        ffmpeg.input(audio_path.as_posix()).output(
            wav_audio_path.as_posix(), ar="16000", ac=1, acodec="pcm_s16le"
        ).overwrite_output().run()
        return wav_audio_path

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        h, m, s = time_str.split(":")
        seconds = int(h) * 3600 + int(m) * 60 + float(s)
        return round(seconds, 2)

    def _parse_whisper_line(self, line: str) -> interfaces.WhisperSegment:
        pattern = (
            r"\[(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\]\s{2}(.*)"
        )
        match = re.match(pattern, line)
        if match:
            start_time, end_time, text = match.groups()
            return interfaces.WhisperSegment(
                start=self._time_to_seconds(start_time),
                end=self._time_to_seconds(end_time),
                text=text,
            )
        raise CannotParseWhisperCppLineException(
            f'Cannot parse whisper.cpp line: "{line}"'
        )

    def transcribe(
        self, audio_path: Path, initial_prompt: str
    ) -> typing.Iterable[interfaces.WhisperSegment]:
        wav_audio_path = self._convert_audio_to_wav(audio_path=audio_path)
        proc = subprocess.Popen(
            [
                self.whisper_cpp_executable,
                "-m",
                self.whisper_cpp_model,
                "-f",
                wav_audio_path,
                "--prompt",
                initial_prompt,
            ],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        if proc.stdout is not None:
            for line in iter(proc.stdout.readline, ""):
                if line in ["", "\n"]:
                    continue
                yield self._parse_whisper_line(line)

        output, error = proc.communicate()
        if proc.returncode != 0:
            raise WhisperCppReturnNonZero(
                f'whisper.cpp command returned errored. output: "{output}", error: "{error}"'
            )

        logger.info(error)
