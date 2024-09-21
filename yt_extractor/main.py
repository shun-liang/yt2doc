import tempfile
import typing
import logging

import typer
import faster_whisper

from enum import Enum
from pathlib import Path

from wtpsplit import SaT

from yt_extractor.youtube.yt_video_info_extractor import YtVideoInfoExtractor
from yt_extractor.transcription.transcriber import Transcriber
from yt_extractor.transcription import interfaces as transcription_interfaces
from yt_extractor.transcription.whisper_cpp_adapter import WhisperCppAdapter
from yt_extractor.transcription.faster_whisper_adapter import FasterWhisperAdapter
from yt_extractor.extraction.file_cache import FileCache
from yt_extractor.extraction import interfaces as extraction_interfaces
from yt_extractor.extraction.extractor import Extractor
from yt_extractor.formatting.formatter import MarkdownFormatter
from yt_extractor.writer import IOWriter


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)

DEFAULT_CACHE_PATH = Path.home() / ".yt-extractor"


class WhisperBackend(str, Enum):
    faster_whisper = "faster_whisper"
    whisper_cpp = "whisper_cpp"


def main(
    video_url: typing.Optional[str] = typer.Option(
        None, "--video", help="URL of the video to extract"
    ),
    playlist_url: typing.Optional[str] = typer.Option(
        None, "--playlist", help="URL of the playlist to extract"
    ),
    output_target: typing.Optional[str] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path",
    ),
    whisper_backend: WhisperBackend = WhisperBackend.faster_whisper,
    faster_whisper_model_size: typing.Optional[str] = typer.Option(
        None, "--whisper-model", help="Whisper model to use for transcription"
    ),
    faster_whisper_compute_type: typing.Optional[str] = typer.Option(
        None,
        "--whisper-compute-type",
        help="Whisper compute type to use for transcription",
    ),
    faster_whisper_device: typing.Optional[str] = typer.Option(
        None, "--whisper-device", help="Whisper device type to use for transcription"
    ),
    whisper_cpp_executable: typing.Annotated[
        typing.Optional[Path], typer.Option()
    ] = None,
    whisper_cpp_model: typing.Annotated[typing.Optional[Path], typer.Option()] = None,
    skip_cache: typing.Annotated[
        bool,
        typer.Option("--skip-cache", help="If should skip reading from cache"),
    ] = False,
) -> None:
    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)

    whisper_adapter: transcription_interfaces.IWhisperAdapter
    meta: extraction_interfaces.MetaDict

    io_writer = IOWriter()

    if whisper_backend is WhisperBackend.faster_whisper:
        if not faster_whisper_model_size:
            faster_whisper_model_size = "base"

        if not faster_whisper_compute_type:
            faster_whisper_compute_type = "int8"

        if not faster_whisper_device:
            faster_whisper_device = "cpu"

        faster_whisper_model = faster_whisper.WhisperModel(
            model_size_or_path=faster_whisper_model_size,
            device=faster_whisper_device,
            compute_type=faster_whisper_compute_type,
        )
        whisper_adapter = FasterWhisperAdapter(whisper_model=faster_whisper_model)
        meta = {
            "whisper_backend": whisper_backend,
            "faster_whisper_model_size": faster_whisper_model_size,
            "faster_whisper_compute_type": faster_whisper_compute_type,
            "faster_whisper_device": faster_whisper_device,
        }
    else:
        if whisper_cpp_executable is None:
            typer.echo(f"--whisper-cpp-executable must be provided.", err=True)
            raise typer.Abort()
        if whisper_cpp_model is None:
            typer.echo(f"--whisper-cpp-model must be provided.", err=True)
            raise typer.Abort()
        whisper_adapter = WhisperCppAdapter(
            whisper_cpp_executable=whisper_cpp_executable,
            whisper_cpp_model=whisper_cpp_model,
        )
        meta = {
            "whisper_backend": whisper_backend,
            "whisper_cpp_executable": whisper_cpp_executable.resolve().as_posix(),
            "whisper_cpp_model": whisper_cpp_model.resolve().as_posix(),
        }

    file_cache = FileCache(
        cache_dir=DEFAULT_CACHE_PATH,
        meta=meta,
    )

    sat = SaT("sat-3l")
    formatter = MarkdownFormatter(sat=sat)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        video_info_extractor = YtVideoInfoExtractor(temp_dir=temp_dir)
        transcriber = Transcriber(
            temp_dir=temp_dir,
            whisper_adapter=whisper_adapter,
        )
        transcript_extractor = Extractor(
            video_info_extractor=video_info_extractor,
            transcriber=transcriber,
            file_cache=file_cache,
        )

        if video_url:
            typer.echo(f"extracting video {video_url}", err=True)

            transcript_by_chapter = transcript_extractor.extract_by_chapter(
                video_url=video_url, skip_cache=skip_cache
            )
            formatted_transcript = formatter.format_chaptered_transcript(
                chaptered_transcript=transcript_by_chapter
            )
            io_writer.write_video_transcript(
                output_target=output_target, formatted_transcript=formatted_transcript
            )

        elif playlist_url:
            typer.echo(f"extracting playlist {playlist_url}", err=True)
            chaptered_transcribed_playlist = (
                transcript_extractor.extract_playlist_by_chapter(
                    playlist_url=playlist_url, skip_cache=skip_cache
                )
            )
            formatted_playlist = formatter.format_chaptered_playlist_transcripts(
                chaptered_playlist=chaptered_transcribed_playlist
            )
            io_writer.write_playlist(
                output_target=output_target, formatted_playlist=formatted_playlist
            )
        else:
            typer.echo("Please provide either --video or --playlist option", err=True)


if __name__ == "__main__":
    typer.run(main)
