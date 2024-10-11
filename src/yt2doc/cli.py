import tempfile
import typing
import logging

import typer

from enum import Enum
from pathlib import Path

import faster_whisper

from yt2doc.writer import IOWriter
from yt2doc.extraction import interfaces as extraction_interfaces
from yt2doc.transcription.interfaces import IWhisperAdapter
from yt2doc.transcription.faster_whisper_adapter import FasterWhisperAdapter
from yt2doc.transcription.whisper_cpp_adapter import WhisperCppAdapter
from yt2doc.factories import get_yt2doc


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)


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
    sat_model: str = typer.Option(
        "sat-3l", "--sat-model", help="Segment Any Text model"
    ),
    llm_model: typing.Optional[str] = typer.Option(
        None,
        "--llm-model",
        help="LLM model for finding text boundaries and title generation",
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
) -> None:
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

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        yt2doc = get_yt2doc(
            whisper_adapter=whisper_adapter,
            meta=meta,
            sat_model=sat_model,
            segment_unchaptered=segment_unchaptered,
            llm_model=llm_model,
            temp_dir=temp_dir,
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


app = typer.Typer()
app.command()(main)

if __name__ == "__main__":
    app()
