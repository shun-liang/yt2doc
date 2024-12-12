import ast
import tempfile
import typing
import logging

import typer

from enum import Enum
from pathlib import Path
from importlib.metadata import version

import faster_whisper

from yt2doc.writer import IOWriter
from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.transcription.interfaces import IWhisperAdapter
from yt2doc.transcription.faster_whisper_adapter import FasterWhisperAdapter
from yt2doc.transcription.whisper_cpp_adapter import WhisperCppAdapter
from yt2doc.factories import get_yt2doc


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)


class MalformedYtDlpOpts(Exception):
    pass


class WhisperBackend(str, Enum):
    faster_whisper = "faster_whisper"
    whisper_cpp = "whisper_cpp"


def _is_dict_of_str_any(
    value: typing.Any,
) -> typing.TypeGuard[typing.Dict[str, typing.Any]]:
    return isinstance(value, dict) and all(isinstance(key, str) for key in value)


def main(
    video_url: typing.Optional[str] = typer.Option(
        None, "--video", "--audio", help="URL of the video to extract"
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
    sat_model: str = typer.Option(
        "sat-3l", "--sat-model", help="Segment Any Text model"
    ),
    llm_model: typing.Optional[str] = typer.Option(
        None,
        "--llm-model",
        help="LLM model for finding text boundaries and title generation",
    ),
    llm_server: str = typer.Option(
        "http://localhost:11434/v1",  # by default use  Ollama
        "--llm-server",
        help="URL of LLM server for finding text boundaries and title generation",
    ),
    llm_api_key: str = typer.Option(
        "ollama",
        "--llm-api-key",
        help="API key for the LLM server; No need to set if using local Ollama server",
    ),
    to_timestamp_paragraphs: bool = typer.Option(
        False,
        "--timestamp-paragraphs",
        help="Prepend timestamp to paragraphs",
    ),
    add_table_of_contents: bool = typer.Option(
        False,
        "--add-table-of-contents",
        help="Add table of contents at the beginning of the document",
    ),
    skip_cache: typing.Annotated[
        bool,
        typer.Option("--skip-cache", help="If should skip reading from cache"),
    ] = False,
    segment_unchaptered: typing.Annotated[
        bool,
        typer.Option(
            "--segment-unchaptered", help="Segment unchaptered video by topic"
        ),
    ] = False,
    ignore_source_chapters: typing.Annotated[
        bool,
        typer.Option(
            "--ignore-source-chapters",
            "--ignore-chapters",
            help="Ignore original chapters from the source",
        ),
    ] = False,
    yt_dlp_extra_opts_str: typing.Optional[str] = typer.Option(
        None,
        "--yt-dlp-extra-opts",
        help="Extra opts to yt-dlp as a string representation of a dictionary",
    ),
    show_version: typing.Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the current version of yt2doc",
        ),
    ] = False,
) -> None:
    if show_version:
        typer.echo(version("yt2doc"))
        return

    io_writer = IOWriter()

    whisper_adapter: IWhisperAdapter
    meta: extraction_interfaces.MetaDict

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
            typer.echo("--whisper-cpp-executable must be provided.", err=True)
            raise typer.Abort()
        if whisper_cpp_model is None:
            typer.echo("--whisper-cpp-model must be provided.", err=True)
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

    if yt_dlp_extra_opts_str is None:
        yt_dlp_extra_opts = {}
    else:
        try:
            yt_dlp_extra_opts = ast.literal_eval(yt_dlp_extra_opts_str)
        except ValueError as e:
            raise MalformedYtDlpOpts(
                f"ValueError when trying to parse --yt-dlp-extra-opts: f{e}"
            )

    if not _is_dict_of_str_any(yt_dlp_extra_opts):
        raise MalformedYtDlpOpts(
            "--yt-dlp-extra-opts is not a string representation of a dictionary"
        )

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        yt2doc = get_yt2doc(
            whisper_adapter=whisper_adapter,
            meta=meta,
            sat_model=sat_model,
            segment_unchaptered=segment_unchaptered,
            ignore_source_chapters=ignore_source_chapters,
            to_timestamp_paragraphs=to_timestamp_paragraphs,
            add_table_of_contents=add_table_of_contents,
            llm_model=llm_model,
            llm_server=llm_server,
            llm_api_key=llm_api_key,
            temp_dir=temp_dir,
            yt_dlp_options=yt_dlp_extra_opts,
        )

        if video_url:
            formatted_transcript = yt2doc.video_to_document(
                video_url=video_url, skip_cache=skip_cache
            )
            io_writer.write_video_transcript(
                output_target=output_target, formatted_transcript=formatted_transcript
            )
        elif playlist_url:
            formatted_playlist = yt2doc.playlist_to_documents(
                playlist_url=playlist_url, skip_cache=skip_cache
            )
            io_writer.write_playlist(
                output_target=output_target, formatted_playlist=formatted_playlist
            )
        else:
            typer.echo("Please provide either --video or --playlist option", err=True)


app = typer.Typer(pretty_exceptions_enable=False)
app.command()(main)

if __name__ == "__main__":
    app()
