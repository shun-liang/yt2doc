# yt2doc

yt2doc transcribes videos online into readable Markdown documents.

Supported video sources:
* YouTube
* Twitter

yt2doc is meant to work fully locally, without invoking any external API. The OpenAI SDK dependency is required solely to interact with [Ollama](https://github.com/ollama/ollama).

## Why

There have been many existing projects that transcribe YouTube videos with Whisper and its variants, but most of them aimed to generate subtitles, while I had not found one that priortises readability. Whisper does not generate line break in its transcription, so transcribing a 20 mins long video without any post processing would give you a huge piece of text, without any line break or topic segmentation. This project aims to transcribe videos with that post processing. 

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

Among smaller size models, `gemma2:9b`, `llama3.1:8b`, and `qwen 2.5:7b` work reasonably well.

By default, yt2doc uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) as transcription backend. You can run yt2doc with different faster-whisper configs (model size, device, compute type etc):

```
yt2doc --video <video-url> --whisper-model <model-name> --whisper-device <cpu|cuda|auto> --whisper-compute-type <compute_type>
```

For the meaning and choices of `--whisper-model`, `--whisper-device` and `--whisper-compute-type`, please refer to this [comment](https://github.com/SYSTRAN/faster-whisper/blob/v1.0.3/faster_whisper/transcribe.py#L101-L127) of faster-whisper.


If you are running yt2doc on Apple Silicon, [whisper.cpp](https://github.com/ggerganov/whisper.cpp) gives much faster performance as it supports the Apple GPU. (A hacky) Support for whisper.cpp has been implemented:

```
yt2doc --video --whisper-backend whisper_cpp --whisper-cpp-executable <path-to-whisper-cpp-executable>  --whisper-cpp-model <path-to-whisper-cpp-model>
```

See https://github.com/shun-liang/yt2doc/issues/15 for more info on whisper.cpp integration.


yt2doc uses [Segment Any Text (SaT)](https://github.com/segment-any-text/wtpsplit) to segment the transcript into sentences and paragraphs. You can change the SaT model:
```
yt2doc --video <video-url> --sat-model <sat-model>
```

List of available SaT models [here](https://github.com/segment-any-text/wtpsplit?tab=readme-ov-file#available-models).

## TODOs
* Tests and evaluation
* Better whisper prompting strategy (right now hugely depend on the title and the description of the video).
* Better support for non-English languages
