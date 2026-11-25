from collections.abc import Sequence
from dataclasses import dataclass

PAUSE_SECONDS = 1.5


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    text: str

    def to_dict(self) -> dict:
        return {"start": self.start, "end": self.end, "text": self.text}

    @classmethod
    def from_dict(cls, data: dict) -> "Segment":
        return cls(float(data["start"]), float(data["end"]), str(data["text"]))


@dataclass(frozen=True)
class TimedWords:
    words: list[str]
    times: list[float]
    pause_after: frozenset[int]


def timed_words(
    segments: Sequence[Segment], pause_seconds: float = PAUSE_SECONDS
) -> TimedWords:
    words: list[str] = []
    times: list[float] = []
    pause_after: set[int] = set()
    for segment, following in zip(segments, [*segments[1:], None]):
        segment_words = segment.text.split()
        words.extend(segment_words)
        times.extend([segment.start] * len(segment_words))
        if words and following is not None and following.start - segment.end >= pause_seconds:
            pause_after.add(len(words) - 1)
    return TimedWords(words, times, frozenset(pause_after))

