from collections.abc import Sequence
from dataclasses import dataclass

PAUSE_SECONDS = 1.5


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class SpokenWords:
    words: list[str]
    pause_after: frozenset[int]


def spoken_words(
    segments: Sequence[Segment], pause_seconds: float = PAUSE_SECONDS
) -> SpokenWords:
    words: list[str] = []
    pause_after: set[int] = set()
    for segment, following in zip(segments, [*segments[1:], None]):
        words.extend(segment.text.split())
        if words and following is not None and following.start - segment.end >= pause_seconds:
            pause_after.add(len(words) - 1)
    return SpokenWords(words, frozenset(pause_after))
