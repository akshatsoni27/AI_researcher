from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)


REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)


def generate_pdf_report(
    report: str,
    filename: str = "research_report.pdf",
) -> str:
    """
    Convert the generated research report into a PDF.
    """

    output_path = REPORTS_DIR / filename

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="MIMIR Report",
        author="MIMIR",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        spaceBefore=14,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        leading=15,
        spaceAfter=8,
    )

    story = []

    lines = report.splitlines()

    first_title = True

    for line in lines:

        line = line.strip()

        if not line:
            story.append(Spacer(1, 6))
            continue

        # Main title
        if line.startswith("# ") and first_title:

            title = line[2:].strip()

            story.append(
                Paragraph(
                    title,
                    title_style,
                )
            )

            first_title = False

        # Section heading
        elif line.startswith("## "):

            heading = line[3:].strip()

            story.append(
                Paragraph(
                    heading,
                    heading_style,
                )
            )

        # Subheading
        elif line.startswith("### "):

            heading = line[4:].strip()

            story.append(
                Paragraph(
                    heading,
                    styles["Heading3"],
                )
            )

        # Bullet
        elif line.startswith("- "):

            bullet = line[2:].strip()

            story.append(
                Paragraph(
                    f"• {bullet}",
                    body_style,
                )
            )

        # Numbered list
        elif len(line) > 2 and line[0].isdigit() and ". " in line[:4]:

            story.append(
                Paragraph(
                    line,
                    body_style,
                )
            )

        # Normal paragraph
        else:

            # Basic escaping for ReportLab XML.
            line = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            story.append(
                Paragraph(
                    line,
                    body_style,
                )
            )

    document.build(story)

    return str(output_path)