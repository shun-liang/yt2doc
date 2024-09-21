import typing

from pathlib import Path

from yt_extractor.formatting import interfaces as formatting_interfaces


class IOException(Exception):
    pass


class IOWriter:
    def write_video_transcript(
        self,
        output_target: typing.Optional[str],
        formatted_transcript: formatting_interfaces.FormattedTranscript,
    ) -> None:
        if output_target is None or output_target == "-":
            print(formatted_transcript.transcript + "\n")
            return

        output_path = Path(output_target)
        if not output_path.exists():
            raise IOException(f"Path {output_target} does not exist.")
        if output_path.is_dir():
            file_path = output_path / f"{formatted_transcript.title}.md"
        else:
            file_path = output_path

        with open(file_path, "w") as f:
            f.write(formatted_transcript.transcript)

    def write_playlist(
        self,
        output_target: typing.Optional[str],
        formatted_playlist: formatting_interfaces.FormattedPlaylist,
    ) -> None:
        if output_target is None or output_target == "-":
            print(formatted_playlist.title + "\n\n")
            print(
                "\n\n".join(
                    [
                        transcript.transcript
                        for transcript in formatted_playlist.transcripts
                    ]
                )
            )
            return

        output_path = Path(output_target)
        if not output_path.exists():
            raise IOException(f"Path {output_target} does not exist.")

        if output_path.is_dir():
            for transcript in formatted_playlist.transcripts:
                file_path = output_path / f"{transcript.title}.md"
                with open(file_path, "w") as f:
                    f.write(transcript.transcript)
        else:
            with open(output_path, "w") as f:
                f.write(
                    "\n\n".join(
                        [
                            transcript.transcript
                            for transcript in formatted_playlist.transcripts
                        ]
                    )
                )
