import typer
import tempfile

from typing import Optional
from pathlib import Path

from faster_whisper import WhisperModel

from yt_extractor.yt_dlp_adapter import YtDlpAdapter
from yt_extractor.whisper_adapter import WhisperAdapter

app = typer.Typer()

@app.command()
def extract(
    video: Optional[str] = typer.Option(None, "--video", help="URL of the video to extract"),
    playlist: Optional[str] = typer.Option(None, "--playlist", help="URL of the playlist to extract")
):

    whisper_model = WhisperModel(model_size_or_path="base", device="cpu")
    whisper_adapter = WhisperAdapter(model=whisper_model)

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        yt_dlp_adapter = YtDlpAdapter(temp_dir=temp_dir)

        if video:
            typer.echo(f"extracting video {video}", err=True)
            video_info = yt_dlp_adapter.extract_video_info(video_url=video)
            transcript = whisper_adapter.transcribe(audio_path=video_info.audio_path)
            typer.echo(transcript)
        elif playlist:
            typer.echo(f"extracting playlist {playlist}", err=True)
        else:
            typer.echo("Please provide either --video or --playlist option", err=True)

@app.command()
def summarize(
    video: Optional[str] = typer.Option(None, "--video", help="URL of the video to summarize"),
    playlist: Optional[str] = typer.Option(None, "--playlist", help="URL of the playlist to summarize")
):
    if video:
        typer.echo(f"summarizing video {video}", err=True)
    elif playlist:
        typer.echo(f"summarizing playlist {playlist}", err=True)
    else:
        typer.echo("Please provide either --video or --playlist option", err=True)

if __name__ == "__main__":
    app()