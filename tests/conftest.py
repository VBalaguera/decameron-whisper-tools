from decameron.engine import Transcription
from decameron.segments import Segment

SAMPLE_SEGMENTS = [
    Segment(0.0, 3.0, "Hola, buenos días."),
    Segment(3.0, 6.0, "Hoy vamos a probar la herramienta."),
    Segment(9.0, 12.0, "Después de una pausa larga, seguimos."),
]


class FakeEngine:
    def __init__(self, segments):
        self.segments = segments
        self.calls = []
        self.paths = []

    def transcribe(self, audio, model, language, prompt, verbose):
        self.calls.append((audio.name, model, language))
        self.paths.append(audio)
        return Transcription(self.segments, "en")
