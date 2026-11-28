from decameron import transcribe

from conftest import SAMPLE_SEGMENTS, FakeEngine


def run(monkeypatch, engine, *args):
    monkeypatch.setattr(transcribe, "WhisperEngine", lambda: engine)
    return transcribe.main([str(arg) for arg in args])


def audio_file(folder):
    path = folder / "nota.m4a"
    path.write_bytes(b"audio")
    return path


def test_output_folder_is_created_and_holds_the_pdf(tmp_path, monkeypatch):
    audio = audio_file(tmp_path)
    folder = tmp_path / "pdf" / "2026"
    assert run(monkeypatch, FakeEngine(SAMPLE_SEGMENTS), audio, "--output", folder) == 0
    assert (folder / "nota.pdf").is_file()
    assert not (tmp_path / "nota.pdf").exists()


def test_missing_audio_fails_but_the_others_are_transcribed(tmp_path, monkeypatch, capsys):
    audio = audio_file(tmp_path)
    engine = FakeEngine(SAMPLE_SEGMENTS)
    assert run(monkeypatch, engine, tmp_path / "missing.m4a", audio) == 1
    assert [call[0] for call in engine.calls] == ["nota.m4a"]
    assert (tmp_path / "nota.pdf").is_file()
    assert "missing.m4a' does not exist" in capsys.readouterr().err


def test_audio_without_speech_saves_nothing(tmp_path, monkeypatch, capsys):
    audio = audio_file(tmp_path)
    assert run(monkeypatch, FakeEngine([]), audio) == 0
    assert not (tmp_path / "nota.pdf").exists()
    assert "no speech found in 'nota.m4a'" in capsys.readouterr().err


def test_existing_pdf_without_terminal_is_skipped(tmp_path, monkeypatch, capsys):
    audio = audio_file(tmp_path)
    pdf = tmp_path / "nota.pdf"
    pdf.write_bytes(b"old")
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    engine = FakeEngine(SAMPLE_SEGMENTS)
    assert run(monkeypatch, engine, audio) == 0
    assert engine.calls == []
    assert pdf.read_bytes() == b"old"
    assert "Skipped" in capsys.readouterr().err
