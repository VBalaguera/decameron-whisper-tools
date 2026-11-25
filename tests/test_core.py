import random

from decameron.paragraphs import build_paragraphs, paragraph_spans, paragraphs_from_segments, sentence_ends
from decameron.segments import spoken_words

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
