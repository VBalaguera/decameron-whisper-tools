import io
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient
from pypdf import PdfReader

from decameron.engine import DEFAULT_LANGUAGE, DEFAULT_MODEL, MODELS
from decameron.server import create_app

from conftest import SAMPLE_SEGMENTS, FakeEngine


class FailingEngine(FakeEngine):
    def transcribe(self, audio, model, language, prompt, verbose):
        raise RuntimeError("out of memory")


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
    dot_dot = client.post("/api/transcribe", files={"audio": ("..", b"audio", "audio/mp4")})
    assert dot_dot.status_code == 400
    bad_model = client.post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}, data={"model": "huge"}
    )
    assert bad_model.status_code == 400
    silent = TestClient(create_app(FakeEngine([]))).post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}
    )
    assert silent.status_code == 422


def test_options_returns_models_and_defaults():
    response = TestClient(create_app(FakeEngine(SAMPLE_SEGMENTS))).get("/api/options")
    assert response.status_code == 200
    assert response.json() == {"models": list(MODELS), "model": DEFAULT_MODEL, "language": DEFAULT_LANGUAGE}


def test_transcribe_deletes_the_temporary_folder():
    engine = FakeEngine(SAMPLE_SEGMENTS)
    response = TestClient(create_app(engine)).post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}
    )
    assert response.status_code == 200
    audio = engine.paths[0]
    assert not audio.exists()
    assert not audio.parent.exists()


def test_transcribe_keeps_the_audio_inside_the_temporary_folder():
    engine = FakeEngine(SAMPLE_SEGMENTS)
    response = TestClient(create_app(engine)).post(
        "/api/transcribe", files={"audio": ("../../nota.m4a", b"audio", "audio/mp4")}
    )
    assert response.status_code == 200
    audio = engine.paths[0]
    assert audio.name == "nota.m4a"
    assert audio.parent.parent == Path(tempfile.gettempdir())


def test_transcribe_reports_engine_errors():
    response = TestClient(create_app(FailingEngine(SAMPLE_SEGMENTS))).post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "Error transcribing 'nota.m4a': out of memory"


def test_transcribe_checks_last_modified_only_when_given():
    client = TestClient(create_app(FakeEngine(SAMPLE_SEGMENTS)))
    without = client.post("/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")})
    assert without.status_code == 200
    not_a_number = client.post(
        "/api/transcribe", files={"audio": ("nota.m4a", b"audio", "audio/mp4")}, data={"last_modified": "abc"}
    )
    assert not_a_number.status_code == 422


def test_transcribe_passes_title_and_language():
    engine = FakeEngine(SAMPLE_SEGMENTS)
    response = TestClient(create_app(engine)).post(
        "/api/transcribe",
        files={"audio": ("nota.m4a", b"audio", "audio/mp4")},
        data={"model": "tiny", "language": "es", "title": "Entrevista"},
    )
    assert response.status_code == 200
    assert engine.calls == [("nota.m4a", "tiny", "es")]
    text = PdfReader(io.BytesIO(response.content)).pages[0].extract_text()
    assert "Entrevista" in text
    assert "detectado" not in text
