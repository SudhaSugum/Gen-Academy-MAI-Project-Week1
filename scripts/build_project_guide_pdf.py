"""Render the current product documentation as the project guide PDF."""

from __future__ import annotations

import re
import sys
from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "PRODUCT_DOCUMENTATION.md"
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "Ecommerce_ROI_Dashboard_Project_Guide.pdf"
NAVY = colors.HexColor("#10263D")
TEAL = colors.HexColor("#0FAF9B")
INK = colors.HexColor("#192434")
MUTED = colors.HexColor("#5E6B7A")
PALE = colors.HexColor("#F1F5F8")
RULE = colors.HexColor("#D8E0E8")


def plain_ascii(text: str) -> str:
    substitutions = {
        "–": "-", "—": "-", "−": "-", "·": " | ", "×": "x", "÷": "/",
        "’": "'", "‘": "'", "“": '"', "”": '"', "≥": ">=", "≤": "<=",
        "→": "->", "•": "-", "…": "...", "€": "EUR", "¥": "JPY",
    }
    for source, replacement in substitutions.items():
        text = text.replace(source, replacement)
    return text.encode("ascii", "ignore").decode("ascii")


def inline_markup(text: str) -> str:
    text = escape(plain_ascii(text))
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#147D78">\1</link>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle(
            "GuideH1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=20,
            leading=25, textColor=NAVY, spaceBefore=17, spaceAfter=10, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "GuideH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14,
            leading=18, textColor=NAVY, spaceBefore=13, spaceAfter=6, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "GuideH3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.5,
            leading=14, textColor=TEAL, spaceBefore=9, spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "GuideBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2,
            leading=13, textColor=INK, spaceAfter=6, alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "GuideBullet", parent=base["BodyText"], fontName="Helvetica", fontSize=9.1,
            leading=12.5, textColor=INK, spaceAfter=3,
        ),
        "table": ParagraphStyle(
            "GuideTable", parent=base["BodyText"], fontName="Helvetica", fontSize=8.1,
            leading=10.5, textColor=INK, spaceAfter=0,
        ),
        "table_header": ParagraphStyle(
            "GuideTableHeader", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=8.1,
            leading=10.5, textColor=colors.white, spaceAfter=0,
        ),
        "code": ParagraphStyle(
            "GuideCode", parent=base["Code"], fontName="Courier", fontSize=8,
            leading=10, textColor=INK,
        ),
    }


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_flowables(markdown: str, styles, frame_width: float):
    lines = markdown.splitlines()
    story = []
    index = 0
    in_code = False
    code_lines = []
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                code_text = plain_ascii("\n".join(code_lines))
                story.append(Preformatted(code_text, styles["code"], maxLineLength=90))
                story.append(Spacer(1, 6))
                code_lines = []
                in_code = False
            else:
                in_code = True
            index += 1
            continue
        if in_code:
            code_lines.append(line)
            index += 1
            continue
        if not stripped:
            index += 1
            continue
        if stripped.startswith("# "):
            index += 1
            continue
        if stripped.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw_cells = split_table_row(lines[index])
                if not all(re.fullmatch(r":?-{3,}:?", cell or "-") for cell in raw_cells):
                    rows.append(raw_cells)
                index += 1
            if rows:
                column_count = max(len(row) for row in rows)
                table_data = []
                for row_number, row in enumerate(rows):
                    row = row + [""] * (column_count - len(row))
                    style = styles["table_header"] if row_number == 0 else styles["table"]
                    table_data.append([Paragraph(inline_markup(cell), style) for cell in row])
                available_width = frame_width
                if column_count == 2:
                    widths = [available_width * 0.26, available_width * 0.74]
                else:
                    widths = [available_width / column_count] * column_count
                table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, TEAL),
                    ("LINEBELOW", (0, 1), (-1, -1), 0.35, RULE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                ]))
                story.extend([Spacer(1, 3), table, Spacer(1, 9)])
            continue
        if stripped.startswith("- "):
            items = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                item_text = lines[index].strip()[2:]
                items.append(ListItem(Paragraph(inline_markup(item_text), styles["bullet"]), leftIndent=10))
                index += 1
            story.append(ListFlowable(
                items, bulletType="bullet", start="circle", leftIndent=17,
                bulletFontName="Helvetica", bulletFontSize=5, bulletColor=TEAL,
                spaceBefore=1, spaceAfter=6,
            ))
            continue
        heading = re.match(r"^(#{2,4})\s+(.+)$", stripped)
        if heading:
            level = min(len(heading.group(1)), 4)
            title = plain_ascii(heading.group(2)).strip()
            if level == 2 and title in {
                "Target controls and campaign opportunities",
                "Data quality and downloads",
            }:
                story.append(PageBreak())
            style_name = "h1" if level == 2 else "h2" if level == 3 else "h3"
            story.append(Paragraph(inline_markup(heading.group(2)), styles[style_name]))
            index += 1
            continue

        paragraph_lines = [stripped]
        index += 1
        while index < len(lines):
            next_line = lines[index].strip()
            if (
                not next_line or next_line.startswith(("#", "- ", "|", "```"))
            ):
                break
            paragraph_lines.append(next_line)
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), styles["body"]))
    return story


def draw_cover(canvas, doc):
    page_width, page_height = letter
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, page_width, page_height, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.roundRect(55, page_height - 92, 78, 5, 2, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#D2DDE8"))
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(58, page_height - 190, "PRODUCT AND TECHNICAL GUIDE")
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 31)
    canvas.drawString(58, page_height - 240, "E-commerce ROI")
    canvas.drawString(58, page_height - 278, "Dashboard")
    canvas.setFillColor(colors.HexColor("#D2DDE8"))
    canvas.setFont("Helvetica", 12)
    canvas.drawString(58, page_height - 318, "Product, metrics, data, and current interface guide")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(58, page_height - 375, "Streamlit application | Python, pandas, Plotly")
    canvas.drawString(58, page_height - 391, "Updated October 2026")
    canvas.setStrokeColor(colors.HexColor("#21425E"))
    canvas.setLineWidth(40)
    canvas.circle(page_width + 5, 42, 145, stroke=1, fill=0)
    canvas.setStrokeColor(colors.HexColor("#24576C"))
    canvas.setLineWidth(24)
    canvas.circle(page_width + 5, 42, 100, stroke=1, fill=0)
    canvas.setFillColor(TEAL)
    canvas.circle(page_width - 69, 42, 5, stroke=0, fill=1)
    canvas.restoreState()


def draw_page(canvas, doc):
    canvas.saveState()
    page_width, page_height = letter
    canvas.setFillColor(NAVY)
    canvas.rect(0, page_height - 33, page_width, 33, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(47, page_height - 21, "E-COMMERCE ROI DASHBOARD")
    canvas.setFillColor(MUTED)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(47, 38, page_width - 47, 38)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(47, 25, "Project guide | Synthetic demonstration data")
    canvas.drawRightString(page_width - 47, 25, f"Page {doc.page}")
    canvas.restoreState()


def build(output: Path):
    source_text = SOURCE.read_text(encoding="utf-8")
    page_width, page_height = letter
    left = right = 47
    top = 53
    bottom = 49
    doc = BaseDocTemplate(
        str(output), pagesize=letter, title="E-commerce ROI Dashboard Project Guide",
        author="E-commerce ROI Dashboard", subject="Product, design, metrics, data contract, and implementation guide",
        leftMargin=left, rightMargin=right, topMargin=top, bottomMargin=bottom,
    )
    cover_frame = Frame(left, 0, page_width - left - right, page_height, id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    body_frame = Frame(left, bottom, page_width - left - right, page_height - top - bottom, id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=cover_frame, onPage=draw_cover),
        PageTemplate(id="Body", frames=body_frame, onPage=draw_page),
    ])
    story = [Spacer(1, 1), NextPageTemplate("Body"), PageBreak()]
    story.extend(markdown_flowables(source_text, make_styles(), page_width - left - right))
    doc.build(story)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    build(target)
    print(f"Wrote {target}")
