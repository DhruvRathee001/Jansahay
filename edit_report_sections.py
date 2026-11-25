from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "JanSahay_Project_Report_Complete.docx"
OUTPUT = ROOT / "JanSahay_Project_Report_Final.docx"


def paragraph_text(block):
    return Paragraph(block, document).text.strip()


document = Document(SOURCE)
body = document.element.body
chapter = None
remove_blocks = []

for block in list(body.iterchildren()):
    if block.tag == qn("w:sectPr"):
        continue

    if block.tag == qn("w:p"):
        text = Paragraph(block, document).text.strip()
        xml = block.xml

        if text == "Chapter 6: SOURCE CODE":
            chapter = 6
            continue
        if text == "Chapter 7: PROJECT OUTPUT":
            chapter = 7
            continue
        if text == "Chapter 8: FUNCTIONING OF THE APPLICATION":
            chapter = 8
            continue

        if chapter in (6, 7):
            keep = (
                text.startswith("Figure 6.")
                or text.startswith("Figure 7.")
                or "w:drawing" in xml
            )
            if not keep:
                remove_blocks.append(block)
    elif block.tag == qn("w:tbl") and chapter in (6, 7):
        # Remove the project-output summary table so both chapters contain
        # only their title, screenshots, and figure captions.
        remove_blocks.append(block)

for block in remove_blocks:
    body.remove(block)

# Remove the running header so the report has no text at the top of each page.
for section in document.sections:
    if section.header.paragraphs:
        section.header.paragraphs[0].text = ""
    section.header_distance = Inches(0.15)

# Put the university and department first, followed immediately by the
# DCRUST logo on the cover page.
paragraphs = list(document.paragraphs)
university = next((p for p in paragraphs if p.text.strip().startswith("DEENBANDHU CHHOTU RAM UNIVERSITY")), None)
department = next((p for p in paragraphs if p.text.strip() == "Department of Computer Science and Engineering"), None)
logo_paragraph = next((p for p in paragraphs[:12] if "w:drawing" in p._p.xml), None)
if university is not None and department is not None and logo_paragraph is not None:
    for p in list(document.paragraphs):
        if p._p is university._p:
            break
        if not p.text.strip():
            p._element.getparent().remove(p._element)
    department._p.addnext(logo_paragraph._p)

# Give the declaration and acknowledgements comfortable reading space while
# keeping the front matter compact enough to stay on its intended pages.
section_name = None
for paragraph in document.paragraphs:
    text = paragraph.text.strip()
    if text == "DECLARATION":
        section_name = "declaration"
        continue
    if text == "CERTIFICATE":
        section_name = None
        continue
    if text == "ACKNOWLEDGEMENTS":
        section_name = "acknowledgements"
        continue
    if text == "TABLE OF CONTENTS":
        section_name = "contents"
        continue
    if text == "Chapter 1: INTRODUCTION":
        section_name = None
        continue

    if section_name == "declaration" and paragraph.style.name == "Body Text":
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.paragraph_format.space_after = Pt(9 if text else 4)
    elif section_name == "acknowledgements" and paragraph.style.name == "Body Text":
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.paragraph_format.space_after = Pt(12)
    elif section_name == "contents" and paragraph.style.name == "List Paragraph":
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.paragraph_format.space_after = Pt(8)
        paragraph.paragraph_format.left_indent = Inches(0.2)
        for run in paragraph.runs:
            run.font.size = Pt(14)

document.save(OUTPUT)
print(OUTPUT)
