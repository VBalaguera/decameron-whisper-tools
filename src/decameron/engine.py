from dataclasses import dataclass
from pathlib import Path

from decameron.segments import Segment

MODELS = ("tiny", "base", "small", "medium", "large-v3", "turbo")
DEFAULT_MODEL = "medium"
DEFAULT_LANGUAGE = "es"

AUDIO_EXTENSIONS = frozenset({
    ".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".aac", ".wma", ".aiff", ".aif",
    ".webm", ".mp4", ".mkv", ".mov", ".avi", ".mpeg", ".mpga", ".amr",
})

DEFAULT_PROMPTS = {
    "es": "Hola, buenos días. ¿Qué tal estás? Bien, gracias. Hoy vamos a hablar de "
    "varios temas. Empecemos por el primero.",
    "en": "Hello, good morning. How are you? Fine, thanks. Today we are going to talk "
    "about several topics. Let's start with the first one.",
}


def default_prompt(language: str | None) -> str | None:
    return DEFAULT_PROMPTS.get((language or "").lower())


@dataclass(frozen=True)
class Transcription:
    segments: list[Segment]
    language: str


class WhisperEngine:
    def __init__(self, download_root: Path | None = None) -> None:
        self._download_root = download_root
        self._models: dict[str, object] = {}

    def load(self, model: str):
        if model not in self._models:
            import whisper

            root = str(self._download_root) if self._download_root else None
            self._models[model] = whisper.load_model(model, download_root=root)
        return self._models[model]

    def transcribe(
        self,
        audio: Path,
        model: str = DEFAULT_MODEL,
        language: str | None = DEFAULT_LANGUAGE,
        prompt: str | None = None,
        verbose: bool = False,
    ) -> Transcription:
        whisper_model = self.load(model)
        result = whisper_model.transcribe(
            str(audio),
            language=language or None,
            initial_prompt=prompt,
            fp16=whisper_model.device.type == "cuda",
            verbose=verbose,
        )
        segments = [
            Segment(round(piece["start"], 2), round(piece["end"], 2), piece["text"].strip())
            for piece in result["segments"]
        ]
        return Transcription([segment for segment in segments if segment.text], result["language"])
