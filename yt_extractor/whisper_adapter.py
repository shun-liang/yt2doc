from pathlib import Path

from faster_whisper import WhisperModel

class WhisperAdapter:

    def __init__(self, model: WhisperModel):
        self.model = model

    def transcribe(self, audio_path: Path) -> str:
        segments, info = self.model.transcribe(audio=audio_path)
        return "".join(s.text for s in segments)