import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from decameron.engine import (
    AUDIO_EXTENSIONS,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    MODELS,
    WhisperEngine,
    default_prompt,
)
from decameron.paragraphs import build_paragraphs
from decameron.pdf import save_pdf
from decameron.transcript import timed_words


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decameron-transcribe",
        description="Transcribe audio files with Whisper and save each transcript "
        "as a PDF in paragraphs, next to its audio.",
    )
    parser.add_argument("audio", nargs="+", type=Path, help="Audio file(s) to transcribe")
    parser.add_argument(
        "--model", choices=MODELS, default=DEFAULT_MODEL, help=f"Whisper model (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--language",
        default=DEFAULT_LANGUAGE,
        help=f"Language code such as es or en, or 'auto' to detect it (default: {DEFAULT_LANGUAGE})",
    )
    return parser


def transcribe_to_pdf(
    engine: WhisperEngine, audio: Path, model: str, language: str | None
) -> Path | None:
    segments = engine.transcribe(
        audio, model=model, language=language, prompt=default_prompt(language), verbose=True
    )
    if not segments:
        return None
    timed = timed_words(segments)
    output = audio.with_suffix(".pdf")
    save_pdf(build_paragraphs(timed.words, timed.pause_after), output)
    return output


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    language = None if args.language.lower() == "auto" else args.language
    engine = WhisperEngine()
    failures = 0
    for audio in args.audio:
        if not audio.is_file():
            print(f"Error: '{audio}' does not exist or is not a file.", file=sys.stderr)
            failures += 1
            continue
        if audio.suffix.lower() not in AUDIO_EXTENSIONS:
            print(f"Error: '{audio.name}' is not a supported audio file.", file=sys.stderr)
            failures += 1
            continue
        print(f"\n{audio.name} (model {args.model}, language {language or 'auto'})", flush=True)
        try:
            output = transcribe_to_pdf(engine, audio, args.model, language)
        except KeyboardInterrupt:
            print("\nCancelled.", file=sys.stderr)
            return 130
        except (OSError, RuntimeError, ValueError) as e:
            print(f"Error transcribing '{audio.name}': {e}", file=sys.stderr)
            failures += 1
            continue
        if output is None:
            print(f"Warning: no speech found in '{audio.name}'. Nothing was saved.", file=sys.stderr)
        else:
            print(f"Saved: {output}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
