# yt2doc

yt2doc transcribes videos online into structural documents in Markdown format.

Supported video sources:
* YouTube
* Twitter

## Installation

Install with [pipx](https://github.com/pypa/pipx):

```
pipx install yt2doc
```

Or install with [uv](https://github.com/astral-sh/uv):
```
uv tool install yt2doc
```

## Usage

Get helping information:

```
yt2doc --help
```

To transcribe a video (on YouTube or Twitter) into a document:

```
yt2doc --video <video-url>
```

To save your transcription:

```
yt2doc --video <video-url> -o some_dir/transcription.md
```

To transcribe all videos from a YouTube playlist:

```
yt2doc --playlist <playlist-url> -o some_dir
```

([Ollama](https://github.com/ollama/ollama) Required) If the video is not chaptered, you can chapter it and add headings to each chapter:

```
yt2doc --video <video-url> --segment-unchaptered --llm-model <model-name>
```

`llama 3.1:8b, qwen2.5 7b, gemma 9b` are among the smaller models that perform reasonably good.

For MacOS devices running Apple Silicon, (a hacky) support for [whisper.cpp](https://github.com/ggerganov/whisper.cpp) is supported:

```
yt2doc --video --whisper-backend whisper_cpp --whisper-cpp-executable <path-to-whisper-cpp-executable>  --whisper-cpp-model <path-to-whisper-cpp-model>
```

yt2doc uses [Segment Any Text (SaT)](https://github.com/segment-any-text/wtpsplit) to segment the transcript into sentences and paragraphs. You can change the SaT model:
```
yt2doc --video <video-url> --sat-model <sat-model>
```

List of available SaT models [here](https://github.com/segment-any-text/wtpsplit?tab=readme-ov-file#available-models).

## TODOs
* Tests and evaluation
* Better whisper prompting strategy (right now hugely depend on the title and the description of the video).
* Better support for non-English languages