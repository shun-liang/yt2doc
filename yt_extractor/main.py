import tempfile
import typing

import typer

from pathlib import Path

from faster_whisper import WhisperModel

from yt_extractor.timer import Timer
from yt_extractor.yt_dlp_adapter import YtDlpAdapter
from yt_extractor.whisper_adapter import WhisperAdapter
from yt_extractor.file_cache import FileCache
from yt_extractor.transcript_extractor import TranscriptExtractor


app = typer.Typer()

DEFAULT_CACHE_PATH = Path.home() / ".yt-extractor"


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
    whisper_model_size: typing.Optional[str] = typer.Option(
        None, "--whisper-model", help="Whisper model to use for transcription"
    ),
    whisper_compute_type: typing.Optional[str] = typer.Option(
        None,
        "--whisper-compute-type",
        help="Whisper compute type to use for transcription",
    ),
    whisper_device: typing.Optional[str] = typer.Option(
        None, "--whisper-device", help="Whisper device type to use for transcription"
    ),
    skip_cache: typing.Annotated[
        bool,
        typer.Option("--skip-cache", help="If should skip reading from cache"),
    ] = False,
) -> None:
    if not whisper_model_size:
        whisper_model_size = "base"

    if not whisper_compute_type:
        whisper_compute_type = "int8"

    if not whisper_device:
        whisper_device = "cpu"

    DEFAULT_CACHE_PATH.mkdir(exist_ok=True)
    file_cache = FileCache(cache_dir=DEFAULT_CACHE_PATH)

    whisper_model = WhisperModel(
        model_size_or_path=whisper_model_size,
        device=whisper_device,
        compute_type=whisper_compute_type,
    )
    whisper_adapter = WhisperAdapter(model=whisper_model)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        yt_dlp_adapter = YtDlpAdapter(temp_dir=temp_dir)

        transcript_extractor = TranscriptExtractor(
            yt_dlp_adapter=yt_dlp_adapter,
            whisper_adapter=whisper_adapter,
            file_cache=file_cache,
            meta={
                "whisper_model_size": whisper_model_size,
                "whisper_compute_type": whisper_compute_type,
                "whisper_device": whisper_device,
            },
        )

        if video_url:
            typer.echo(f"extracting video {video_url}", err=True)

            if by_chapter:
                transcript_by_chapter = transcript_extractor.extract_by_chapter(
                    video_url=video_url, skip_cache=skip_cache
                )
                header = f"# {transcript_by_chapter.title}\n\n{video_url}"
                transcript_text = "'\n\n".join(
                    [
                        f"## {chapter.title}\n\n{chapter.text}"
                        for chapter in transcript_by_chapter.chapters
                    ]
                )
                transcript_text = f"{header}\n\n{transcript_text}"

            else:
                transcript = transcript_extractor.extract(
                    video_url=video_url, skip_cache=skip_cache
                )
                transcript_text = (
                    f"# {transcript.title}\n\n{video_url}\n\n{transcript.text}"
                )

            typer.echo(transcript_text)

        elif playlist_url:
            typer.echo(f"extracting playlist {playlist_url}", err=True)
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
