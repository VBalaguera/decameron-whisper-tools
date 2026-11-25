import os
import unicodedata
from collections.abc import Callable, Sequence
from pathlib import Path

PDF_ENCODING = "windows-1252"
WINDOWS_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
UNICODE_FONTS = (
    (Path("/System/Library/Fonts/Supplemental/Arial.ttf"), Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")),
    (WINDOWS_FONTS / "arial.ttf", WINDOWS_FONTS / "arialbd.ttf"),
    (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
)


def _unicode_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _basic_text(text: str) -> str:
    return _unicode_text(text).encode(PDF_ENCODING, errors="replace").decode(PDF_ENCODING)


def setup_font(pdf) -> tuple[str, Callable[[str], str]]:
    for regular, bold in UNICODE_FONTS:
        if regular.is_file():
            pdf.add_font("body", fname=str(regular))
            pdf.add_font("body", style="B", fname=str(bold if bold.is_file() else regular))
            return "body", _unicode_text
    pdf.core_fonts_encoding = PDF_ENCODING
    return "helvetica", _basic_text


def save_pdf(
    paragraphs: Sequence[str],
    path: Path,
    title: str = "",
    details: Sequence[tuple[str, str]] = (),
) -> None:
    from fpdf import FPDF

    pdf = FPDF()
    family, prepare = setup_font(pdf)
    if title:
        pdf.set_title(title)
    pdf.add_page()
    if title:
        pdf.set_font(family, style="B", size=20)
        pdf.multi_cell(0, 9, text=prepare(title), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
    pdf.set_font(family, size=10)
    for label, value in details:
        pdf.cell(34, 6, text=prepare(f"{label}:"))
        pdf.multi_cell(0, 6, text=prepare(value), new_x="LMARGIN", new_y="NEXT")
    if title or details:
        pdf.ln(3)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(6)
    pdf.set_font(family, size=12)
    for paragraph in paragraphs:
        pdf.multi_cell(0, 7, text=prepare(paragraph), align="J", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
    pdf.output(str(path))
