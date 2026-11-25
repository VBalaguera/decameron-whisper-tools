import os
import unicodedata
from collections.abc import Sequence
from pathlib import Path

PDF_ENCODING = "windows-1252"
UNICODE_FONTS = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)


def setup_font(pdf) -> bool:
    for path in UNICODE_FONTS:
        if path.is_file():
            pdf.add_font("body", fname=str(path))
            pdf.set_font("body", size=12)
            return True
    pdf.core_fonts_encoding = PDF_ENCODING
    pdf.set_font("helvetica", size=12)
    return False


def save_pdf(paragraphs: Sequence[str], path: Path) -> None:
    from fpdf import FPDF

    pdf = FPDF()
    unicode_font = setup_font(pdf)
    pdf.add_page()
    for paragraph in paragraphs:
        text = unicodedata.normalize("NFC", paragraph)
        if not unicode_font:
            text = text.encode(PDF_ENCODING, errors="replace").decode(PDF_ENCODING)
        pdf.multi_cell(0, 7, text=text, align="J", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
    pdf.output(str(path))
