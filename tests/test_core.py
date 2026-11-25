import random

from decameron.paragraphs import build_paragraphs, paragraph_spans, sentence_ends
from decameron.transcript import Segment, timed_words

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


def test_timed_words_marks_long_pauses():
    timed = timed_words(SAMPLE_SEGMENTS)
    assert timed.words[:3] == ["Hola,", "buenos", "días."]
    assert timed.times[0] == 0.0 and timed.times[-1] == 9.0
    assert timed.pause_after == {len("Hola, buenos días. Hoy vamos a probar la herramienta.".split()) - 1}


def test_segment_round_trip():
    segment = Segment(1.0, 2.5, "Hola.")
    assert Segment.from_dict(segment.to_dict()) == segment
    assert Segment.from_dict({"start": "1", "end": "2.5", "text": "Hola."}) == segment
