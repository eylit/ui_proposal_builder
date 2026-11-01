"""Proposal helpers: where the pictures go in the text, and the Word (.docx) export."""
import io
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

from theme import BRAND_FONT, DARK

# The proposal text contains these lines on their own; they are swapped for the pictures.
PIC_WEB = "[Picture: Website UI]"
PIC_REPORT = "[Picture: Report Layout]"


def ensure_pictures(text: str) -> str:
    """Make sure both picture lines are present (the model may forget them). Added before the matching section."""
    for token, before in ((PIC_WEB, ("patient report layout",)), (PIC_REPORT, ("sign-off", "sign off"))):
        if token in text:
            continue
        lines = text.splitlines()
        at = next((i for i, line in enumerate(lines) if any(k in line.lower() for k in before)), len(lines))
        lines[at:at] = [token, ""]
        text = "\n".join(lines)
    return text


def split_proposal(text: str) -> list[tuple[str, str]]:
    """Split the proposal into ("text", markdown) chunks and ("web" | "report", "") picture markers."""
    parts, buf = [], []
    for line in text.splitlines():
        kind = {PIC_WEB: "web", PIC_REPORT: "report"}.get(line.strip())
        if kind:
            if buf:
                parts.append(("text", "\n".join(buf)))
                buf = []
            parts.append((kind, ""))
        else:
            buf.append(line)
    if buf:
        parts.append(("text", "\n".join(buf)))
    return parts


def _add_runs(paragraph, text: str) -> None:
    """Add text to a paragraph, turning **bold** pieces into bold runs."""
    for piece in re.split(r"(\*\*.+?\*\*)", text):
        if piece.startswith("**") and piece.endswith("**") and len(piece) > 4:
            paragraph.add_run(piece[2:-2]).bold = True
        elif piece:
            paragraph.add_run(piece)


def build_docx(text: str, pictures: dict[str, bytes], logo: bytes) -> bytes:
    """Build the Word file: logo in the page header, the proposal text, and the two pictures in place."""
    doc = Document()
    for name in ("Normal", "List Bullet", "List Number", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = BRAND_FONT
        if name.startswith("Heading"):
            style.font.color.rgb = RGBColor.from_string(DARK[1:])
    doc.styles["Normal"].font.size = Pt(11)

    header = doc.sections[0].header
    header.paragraphs[0].add_run().add_picture(io.BytesIO(logo), width=Inches(1.8))

    first_heading = True
    for kind, chunk in split_proposal(text):
        if kind != "text":
            doc.add_picture(io.BytesIO(pictures[kind]), width=Inches(6.0))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        for raw in chunk.splitlines():
            line = raw.strip()
            if not line:
                continue
            heading = re.match(r"^#{1,3}\s+(.*)$", line) or re.match(r"^\*\*([^*]+)\*\*:?$", line)
            if heading:
                doc.add_heading(heading.group(1).strip(), level=1 if first_heading else 2)
                first_heading = False
            elif re.match(r"^[-*]\s+", line):
                _add_runs(doc.add_paragraph(style="List Bullet"), re.sub(r"^[-*]\s+", "", line))
            elif re.match(r"^\d+[.)]\s+", line):
                _add_runs(doc.add_paragraph(style="List Number"), re.sub(r"^\d+[.)]\s+", "", line))
            else:
                _add_runs(doc.add_paragraph(), line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
