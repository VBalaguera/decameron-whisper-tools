import random

from pypdf import PdfReader

from decameron import pdf
from decameron.paragraphs import build_paragraphs, paragraph_spans, paragraphs_from_segments, sentence_ends
from decameron.segments import spoken_words
from decameron.transcribe import confirm_overwrite, output_path

from conftest import SAMPLE_SEGMENTS


def test_sentence_ends_respects_ellipsis_pauses():
    assert sentence_ends(["Y", "entonces...", "no", "sé."]) == [False, False, False, True]
    assert sentence_ends(["Fin...", "Otra."]) == [True, True]


def test_paragraphs_never_change_words():
    words = ("Hola, buenos días. Y entonces... no sé. " + "palabra, " * 300 + "fin. Corta.").split()
    paragraphs = build_paragraphs(words, rng=random.Random(1))
    assert " ".join(paragraphs).split() == words
    assert all(len(p.split()) <= 200 for p in paragraphs)
    assert len(paragraphs) > 1


def test_short_tail_joins_previous_paragraph():
    words = ("Uno dos tres. " * 12 + "Fin.").split()
    spans = paragraph_spans(words, rng=random.Random(3))
    assert spans[-1][1] == len(words)
    assert spans[-1][1] - spans[-1][0] >= 1


def test_spoken_words_marks_long_pauses():
    spoken = spoken_words(SAMPLE_SEGMENTS)
    assert spoken.words[:3] == ["Hola,", "buenos", "días."]
    assert spoken.pause_after == {len("Hola, buenos días. Hoy vamos a probar la herramienta.".split()) - 1}


def test_paragraphs_from_segments_keeps_every_word():
    paragraphs = paragraphs_from_segments(SAMPLE_SEGMENTS, random.Random(0))
    assert " ".join(paragraphs).split() == " ".join(s.text for s in SAMPLE_SEGMENTS).split()


def test_pdf_has_header_and_paragraphs(tmp_path):
    path = tmp_path / "out.pdf"
    pdf.save_pdf(
        ["Primer párrafo.", "Segundo párrafo."],
        path,
        title="Título con eñe",
        details=[("Audio", "nota.m4a"), ("Idioma", "es")],
    )
    text = PdfReader(path).pages[0].extract_text()
    for expected in ["Título con eñe", "Audio:", "nota.m4a", "Idioma:", "Primer párrafo.", "Segundo párrafo."]:
        assert expected in text


def test_pdf_without_system_font_replaces_unknown_characters(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf, "UNICODE_FONTS", ())
    path = tmp_path / "out.pdf"
    pdf.save_pdf(["Canción 中"], path, title="Título")
    text = PdfReader(path).pages[0].extract_text()
    assert "Canción ?" in text
    assert "Título" in text


def test_output_path_uses_audio_folder_or_given_folder(tmp_path):
    audio = tmp_path / "grabaciones" / "nota.m4a"
    assert output_path(audio, None) == tmp_path / "grabaciones" / "nota.pdf"
    assert output_path(audio, tmp_path / "pdf") == tmp_path / "pdf" / "nota.pdf"


def test_confirm_overwrite_asks_only_when_pdf_exists(tmp_path, monkeypatch):
    path = tmp_path / "nota.pdf"
    assert confirm_overwrite(path)
    path.write_bytes(b"")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt: "y")
    assert confirm_overwrite(path)
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    assert not confirm_overwrite(path)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert not confirm_overwrite(path)
