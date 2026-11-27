import io
from datetime import datetime

from fastapi.testclient import TestClient
from pypdf import PdfReader

from decameron.engine import Transcription
from decameron.server import create_app

from conftest import SAMPLE_SEGMENTS


class FakeEngine:
    def __init__(self, segments):
        self.segments = segments
        self.calls = []

    def transcribe(self, audio, model, language, prompt, verbose):
        self.calls.append((audio.name, model, language))
        return Transcription(self.segments, "en")


def test_transcribe_returns_pdf_with_audio_date():
    engine = FakeEngine(SAMPLE_SEGMENTS)
    client = TestClient(create_app(engine))
    date = datetime(2026, 10, 12, 9, 30)
    response = client.post(
        "/api/transcribe",
        files={"audio": ("nota.m4a", b"audio", "audio/mp4")},
        data={"model": "tiny", "language": "auto", "last_modified": str(int(date.timestamp() * 1000))},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert engine.calls == [("nota.m4a", "tiny", None)]
    text = PdfReader(io.BytesIO(response.content)).pages[0].extract_text()
    for expected in ["nota", "nota.m4a", "2026-10-12 09:30", "en (detectado)", "Hola, buenos días."]:
        assert expected in text


def test_transcribe_rejects_bad_requests():
    client = TestClient(create_app(FakeEngine(SAMPLE_SEGMENTS)))
    not_audio = client.post("/api/transcribe", files={"audio": ("notas.txt", b"text", "text/plain")})
    assert not_audio.status_code == 400
    bad_model = client.post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}, data={"model": "huge"}
    )
    assert bad_model.status_code == 400
    silent = TestClient(create_app(FakeEngine([]))).post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}
    )
    assert silent.status_code == 422
