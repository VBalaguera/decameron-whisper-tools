import random
import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from decameron.segments import Segment, spoken_words

CLOSERS = "\"'”’»)]"
SENTENCE_END = re.compile(rf"[.!?…][{re.escape(CLOSERS)}]*$")
CLAUSE_END = re.compile(rf"[,;:][{re.escape(CLOSERS)}]*$")


@dataclass(frozen=True)
class ParagraphRules:
    min_sentences: int = 2
    max_sentences: int = 5
    target_words: tuple[int, int] = (70, 120)
    long_sentence: int = 80
    min_tail: int = 25
    soft_max: int = 150
    hard_max: int = 200
    pause_min: int = 40


DEFAULT_RULES = ParagraphRules()


def sentence_ends(words: Sequence[str]) -> list[bool]:
    ends: list[bool] = []
    for i, word in enumerate(words):
        end = bool(SENTENCE_END.search(word))
        if end and word.rstrip(CLOSERS).endswith(("...", "…")):
            following = words[i + 1] if i + 1 < len(words) else ""
            end = not following[:1].islower()
        ends.append(end)
    return ends


def sentence_lengths(ends: Sequence[bool]) -> tuple[list[int], list[int]]:
    length = [0] * len(ends)
    remaining = [0] * len(ends)
    start = 0
    for i in range(len(ends)):
        if ends[i] or i == len(ends) - 1:
            for j in range(start, i + 1):
                length[j] = i + 1 - start
                remaining[j] = i - j
            start = i + 1
    return length, remaining


def paragraph_spans(
    words: Sequence[str],
    pause_after: Collection[int] = frozenset(),
    rng: random.Random | None = None,
    rules: ParagraphRules = DEFAULT_RULES,
) -> list[tuple[int, int]]:
    rng = rng or random.Random()
    ends = sentence_ends(words)
    length, remaining = sentence_lengths(ends)

    spans: list[tuple[int, int]] = []
    start = 0
    sentences = 0
    goal_sentences = rng.randint(rules.min_sentences, rules.max_sentences)
    goal_words = rng.randint(*rules.target_words)

    for i, word in enumerate(words):
        n = i + 1 - start
        clause_end = bool(CLAUSE_END.search(word))
        pause = i in pause_after
        run_on = (
            not ends[i]
            and length[i] >= rules.long_sentence
            and remaining[i] >= rules.min_tail
        )

        if ends[i]:
            sentences += 1
            close = sentences >= goal_sentences or n >= rules.soft_max
        else:
            close = (run_on and n >= goal_words and (clause_end or pause)) or (
                n >= rules.hard_max
            )

        if (
            not close
            and pause
            and n >= rules.pause_min
            and (ends[i] or (run_on and clause_end))
        ):
            close = True

        if close:
            spans.append((start, i + 1))
            start = i + 1
            sentences = 0
            goal_sentences = rng.randint(rules.min_sentences, rules.max_sentences)
            goal_words = rng.randint(*rules.target_words)

    if start < len(words):
        if spans and len(words) - start < rules.min_tail:
            spans[-1] = (spans[-1][0], len(words))
        else:
            spans.append((start, len(words)))
    return spans


def build_paragraphs(
    words: Sequence[str],
    pause_after: Collection[int] = frozenset(),
    rng: random.Random | None = None,
    rules: ParagraphRules = DEFAULT_RULES,
) -> list[str]:
    return [
        " ".join(words[a:b]) for a, b in paragraph_spans(words, pause_after, rng, rules)
    ]


def paragraphs_from_segments(
    segments: Sequence[Segment], rng: random.Random | None = None
) -> list[str]:
    spoken = spoken_words(segments)
    return build_paragraphs(spoken.words, spoken.pause_after, rng)
