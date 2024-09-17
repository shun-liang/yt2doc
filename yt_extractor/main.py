import tempfile
import typing
import logging

import typer

from pathlib import Path

from faster_whisper import WhisperModel
from openai import OpenAI

from yt_extractor.youtube.yt_video_info_extractor import YtVideoInfoExtractor
from yt_extractor.youtube.yt_video_info_processor import YtVideoInfoProcessor
from yt_extractor.transcription.transcriber import Transcriber
from yt_extractor.extraction.file_cache import FileCache
from yt_extractor.extraction.extractor import Extractor
from yt_extractor.extraction.formatter import Formatter


logging.basicConfig(level=logging.INFO)

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
    file_cache = FileCache(
        cache_dir=DEFAULT_CACHE_PATH,
        meta={
            "whisper_model_size": whisper_model_size,
            "whisper_compute_type": whisper_compute_type,
            "whisper_device": whisper_device,
        },
    )

    whisper_model = WhisperModel(
        model_size_or_path=whisper_model_size,
        device=whisper_device,
        compute_type=whisper_compute_type,
    )
    llm_client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # required, but unused
    )

    formatter = Formatter()

    video_info_processor = YtVideoInfoProcessor(
        llm_client=llm_client, llm_model="mistral-nemo"
    )

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        video_info_extractor = YtVideoInfoExtractor(
            temp_dir=temp_dir, video_processor=video_info_processor
        )
        transcriber = Transcriber(
            temp_dir=temp_dir,
            whisper_model=whisper_model,
            llm_client=llm_client,
            llm_model="mistral-nemo",
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
