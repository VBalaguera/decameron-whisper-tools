import argparse
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from decameron.engine import (
    AUDIO_EXTENSIONS,
    DEFAULT_LANGUAGE,
    DEFAULT_MODEL,
    MODELS,
    WhisperEngine,
    default_prompt,
)
from decameron.paragraphs import paragraphs_from_segments
from decameron.pdf import save_pdf

DATE_FORMAT = "%Y-%m-%d %H:%M"


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
    parser.add_argument(
        "--title", help="Title shown at the top of the PDF (default: the audio file name without its extension)"
    )
    return parser


def audio_problem(audio: Path) -> str | None:
    if not audio.is_file():
        return f"'{audio}' does not exist or is not a file."
    if audio.suffix.lower() not in AUDIO_EXTENSIONS:
        return f"'{audio.name}' is not a supported audio file."
    return None


def language_label(requested: str | None, detected: str) -> str:
    return requested if requested else f"{detected} (detectado)"


def pdf_details(audio: Path, model: str, language: str) -> list[tuple[str, str]]:
    return [
        ("Audio", audio.name),
        ("Fecha del audio", datetime.fromtimestamp(audio.stat().st_mtime).strftime(DATE_FORMAT)),
        ("Transcrito el", datetime.now().strftime(DATE_FORMAT)),
        ("Modelo", model),
        ("Idioma", language),
    ]


def transcribe_to_pdf(
    engine: WhisperEngine, audio: Path, model: str, language: str | None, title: str | None = None
) -> Path | None:
    transcription = engine.transcribe(
        audio, model=model, language=language, prompt=default_prompt(language), verbose=True
    )
    if not transcription.segments:
        return None
    output = audio.with_suffix(".pdf")
    save_pdf(
        paragraphs_from_segments(transcription.segments),
        output,
        title=title or audio.stem,
        details=pdf_details(audio, model, language_label(language, transcription.language)),
    )
    return output


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    language = None if args.language.lower() == "auto" else args.language
    engine = WhisperEngine()
    failures = 0
    for audio in args.audio:
        problem = audio_problem(audio)
        if problem:
            print(f"Error: {problem}", file=sys.stderr)
            failures += 1
            continue
        print(f"\n{audio.name} (model {args.model}, language {language or 'auto'})", flush=True)
        try:
            output = transcribe_to_pdf(engine, audio, args.model, language, args.title)
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
