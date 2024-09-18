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
from yt_extractor.transcription.interfaces import IWhisperAdapter
from yt_extractor.transcription.whisper_cpp_adapter import WhisperCppAdapter
from yt_extractor.transcription.faster_whisper_adapter import FasterWhisperAdapter
from yt_extractor.extraction.file_cache import FileCache
from yt_extractor.extraction.interfaces import MetaDict
from yt_extractor.extraction.extractor import Extractor
from yt_extractor.extraction.formatter import Formatter


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)

app = typer.Typer()

DEFAULT_CACHE_PATH = Path.home() / ".yt-extractor"


class WhisperBackend(str, Enum):
    faster_whisper = "faster_whisper"
    whisper_cpp = "whisper_cpp"


@app.command()
def extract(
    video_url: typing.Optional[str] = typer.Option(
        None, "--video", help="URL of the video to extract"
    ),
    playlist_url: typing.Optional[str] = typer.Option(
        None, "--playlist", help="URL of the playlist to extract"
    ),
    by_chapter: typing.Annotated[
        bool,
        typer.Option(
            "--by-chapter", help="If should split the audio by YouTube video chapter"
        ),
    ] = False,
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

    whisper_adapter: IWhisperAdapter
    meta: MetaDict

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
    formatter = Formatter(sat=sat)

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

            if by_chapter:
                transcript_by_chapter = transcript_extractor.extract_by_chapter(
                    video_url=video_url, skip_cache=skip_cache
                )
                logger.info(f"transcript_by_chapter: {transcript_by_chapter}")
                transcript_text = formatter.chaptered_transcript_to_markdown(
                    chaptered_transcript=transcript_by_chapter, is_root=True
                )

            else:
                transcript = transcript_extractor.extract(
                    video_url=video_url, skip_cache=skip_cache
                )
                transcript_text = formatter.transcript_to_markdown(
                    transcript=transcript, is_root=True
                )

            typer.echo(transcript_text)

        elif playlist_url:
            typer.echo(f"extracting playlist {playlist_url}", err=True)
            if by_chapter:
                chaptered_transcribed_playlist = (
                    transcript_extractor.extract_playlist_by_chapter(
                        playlist_url=playlist_url, skip_cache=skip_cache
                    )
                )
                transcripts_text = formatter.chaptered_playlist_transcripts_to_markdown(
                    chaptered_playlist=chaptered_transcribed_playlist
                )
            else:
                transcripts_text = ""

            typer.echo(transcripts_text)

        else:
            typer.echo("Please provide either --video or --playlist option", err=True)


@app.command()
def summarize(
    video: typing.Optional[str] = typer.Option(
        None, "--video", help="URL of the video to summarize"
    ),
    playlist: typing.Optional[str] = typer.Option(
        None, "--playlist", help="URL of the playlist to summarize"
    ),
) -> None:
    if video:
        typer.echo(f"summarizing video {video}", err=True)
    elif playlist:
        typer.echo(f"summarizing playlist {playlist}", err=True)
    else:
        typer.echo("Please provide either --video or --playlist option", err=True)


if __name__ == "__main__":
    app()
