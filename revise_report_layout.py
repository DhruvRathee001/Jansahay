from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "JanSahay_Project_Report_Final.docx"
OUTPUT = ROOT / "JanSahay_Project_Report_Final_Formatted.docx"

TEAL = "2F75B5"
NAVY = "102A43"
GRAY = "5A5A5A"


def remove_element(element):
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def add_bookmark(paragraph, name, bookmark_id):
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), str(bookmark_id))
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def add_pageref(paragraph, bookmark):
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), f"PAGEREF {bookmark} \\h")
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), NAVY)
    rpr.append(color)
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), "22")
    rpr.append(size)
    run.append(rpr)
    text = OxmlElement("w:t")
    text.text = "1"
    run.append(text)
    field.append(run)
    paragraph._p.append(field)


def add_page_field(paragraph):
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run = OxmlElement("w:r")
    text = OxmlElement("w:t")
    text.text = "1"
    run.append(text)
    field.append(run)
    paragraph._p.append(field)


def set_update_fields(document):
    settings = document.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


def insert_paragraph_after(anchor, text="", style=None):
    new_p = OxmlElement("w:p")
    anchor._p.addnext(new_p)
    paragraph = Paragraph(new_p, anchor._parent)
    if style:
        paragraph.style = style
    if text:
        paragraph.add_run(text)
    return paragraph


def format_runs(paragraph, size=11, color=NAVY, bold=False):
    for run in paragraph.runs:
        run.font.name = "Arial"
        run.font.size = Pt(size)
        run.font.color.rgb = RGBColor.from_string(color)
        if bold:
            run.bold = True


def add_index_entry(anchor, label, bookmark, size=11, bold=False):
    paragraph = insert_paragraph_after(anchor, style="Normal")
    paragraph.paragraph_format.tab_stops.add_tab_stop(Inches(6.35), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    paragraph.paragraph_format.space_after = Pt(7)
    paragraph.paragraph_format.line_spacing = 1.25
    paragraph.add_run(label)
    paragraph.add_run("\t")
    add_pageref(paragraph, bookmark)
    format_runs(paragraph, size=size, color=NAVY, bold=bold)
    return paragraph


def replace_certificate(document):
    paragraphs = document.paragraphs
    heading = next(p for p in paragraphs if p.text.strip() == "CERTIFICATE")
    abstract = next(p for p in paragraphs if p.text.strip() == "ABSTRACT")
    current = heading._p.getnext()
    while current is not None and current is not abstract._p:
        next_element = current.getnext()
        remove_element(current)
        current = next_element

    body = insert_paragraph_after(heading, style="Body Text")
    body.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    body.paragraph_format.line_spacing = 1.15
    body.paragraph_format.space_after = Pt(4)
    body.add_run(
        'This is to certify that the project report entitled “JanSahay: An AI-Assisted Personalized Government Service Eligibility and Navigation System” submitted by Dev (23001001022), Devender (23001001023), and Dhruv (23001001024) in partial fulfilment of the requirements for the award of the degree of Bachelor of Technology in Computer Science and Engineering at Deenbandhu Chhotu Ram University of Science and Technology, Murthal, is a record of the candidates’ own work carried out under my supervision and guidance.'
    )
    format_runs(body, size=11, color=NAVY)

    for _ in range(6):
        spacer = insert_paragraph_after(body, style="Normal")
        spacer.paragraph_format.space_after = Pt(3)
        body = spacer

    supervisor = insert_paragraph_after(body, style="Body Text")
    supervisor.paragraph_format.space_after = Pt(0)
    supervisor.add_run("Dr. Dinesh Singh").bold = True
    format_runs(supervisor, size=11, color=NAVY)
    for line in [
        "Project Supervisor",
        "Department of Computer Science and Engineering",
        "DCRUST, Murthal",
    ]:
        p = insert_paragraph_after(supervisor, line, style="Body Text")
        p.paragraph_format.space_after = Pt(0)
        format_runs(p, size=11, color=NAVY)
        supervisor = p
    place = insert_paragraph_after(supervisor, "Place: DCRUST, Murthal", style="Body Text")
    place.paragraph_format.space_before = Pt(54)
    place.paragraph_format.space_after = Pt(10)
    format_runs(place, size=11, color=NAVY)
    date = insert_paragraph_after(place, "Date: November 25, 2026", style="Body Text")
    date.paragraph_format.space_after = Pt(0)
    format_runs(date, size=11, color=NAVY)


def move_cover_logo(document):
    paragraphs = document.paragraphs
    university = next(p for p in paragraphs if p.text.strip().startswith("DEENBANDHU CHHOTU RAM UNIVERSITY"))
    department = next(p for p in paragraphs if p.text.strip() == "Department of Computer Science and Engineering")
    drawing = next((node for node in list(department._p.iter()) if node.tag == qn("w:drawing")), None)
    if drawing is None:
        return
    parent_run = drawing.getparent()
    remove_element(drawing)
    logo_para = insert_paragraph_after(department, style="Normal")
    logo_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = logo_para.add_run()
    run._r.append(drawing)
    department.paragraph_format.space_after = Pt(3)
    logo_para.paragraph_format.space_after = Pt(5)


def replace_contents_and_add_figures(document):
    paragraphs = document.paragraphs
    contents = next(p for p in paragraphs if p.text.strip() == "TABLE OF CONTENTS")
    chapter1 = next(p for p in paragraphs if p.text.strip() == "Chapter 1: INTRODUCTION")
    figure_captions = [p.text.strip() for p in paragraphs if p.text.strip().startswith("Figure ")]

    current = contents._p.getnext()
    while current is not None and current is not chapter1._p:
        next_element = current.getnext()
        remove_element(current)
        current = next_element

    contents.text = "CONTENTS"
    contents.alignment = WD_ALIGN_PARAGRAPH.LEFT
    format_runs(contents, size=18, color=TEAL, bold=True)
    contents.paragraph_format.space_after = Pt(12)

    entries = [
        ("LIST OF FIGURES", "list_of_figures"),
        ("CHAPTER 1: INTRODUCTION", "chapter_1"),
        ("CHAPTER 2: SYSTEM ANALYSIS AND DESIGN", "chapter_2"),
        ("CHAPTER 3: HARDWARE AND SOFTWARE SPECIFICATION", "chapter_3"),
        ("CHAPTER 4: TOOLS AND TECHNOLOGIES USED", "chapter_4"),
        ("CHAPTER 5: CONTROL FLOW OF JANSAHAY", "chapter_5"),
        ("CHAPTER 6: SOURCE CODE", "chapter_6"),
        ("CHAPTER 7: PROJECT OUTPUT", "chapter_7"),
        ("CHAPTER 8: FUNCTIONING OF THE APPLICATION", "chapter_8"),
        ("CHAPTER 9: CONCLUSION AND FUTURE SCOPE", "chapter_9"),
        ("CHAPTER 10: REFERENCES", "chapter_10"),
        ("APPENDIX A: CURATED SCHEME CATALOGUE", "appendix_a"),
        ("APPENDIX B: TEST AND DEMONSTRATION CHECKLIST", "appendix_b"),
    ]
    anchor = contents
    for label, bookmark in entries:
        anchor = add_index_entry(anchor, label, bookmark, size=11, bold=True)

    figures_heading = insert_paragraph_after(anchor, "LIST OF FIGURES", style="Heading 1")
    figures_heading.paragraph_format.page_break_before = True
    figures_heading.paragraph_format.space_after = Pt(12)
    figures_heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    format_runs(figures_heading, size=18, color=TEAL, bold=True)
    add_bookmark(figures_heading, "list_of_figures", 300)
    anchor = figures_heading
    for index, caption in enumerate(figure_captions, start=1):
        bookmark = f"figure_{index}"
        anchor = add_index_entry(anchor, caption, bookmark, size=10.5, bold=False)

    chapter1.paragraph_format.page_break_before = True

    # Attach bookmarks to real chapter headings and figure captions.
    chapter_map = {
        "Chapter 1: INTRODUCTION": "chapter_1",
        "Chapter 2: SYSTEM ANALYSIS AND DESIGN": "chapter_2",
        "Chapter 3: HARDWARE AND SOFTWARE SPECIFICATION": "chapter_3",
        "Chapter 4: TOOLS AND TECHNOLOGIES USED": "chapter_4",
        "Chapter 5: CONTROL FLOW OF JANSAHAY": "chapter_5",
        "Chapter 6: SOURCE CODE": "chapter_6",
        "Chapter 7: PROJECT OUTPUT": "chapter_7",
        "Chapter 8: FUNCTIONING OF THE APPLICATION": "chapter_8",
        "Chapter 9: CONCLUSION AND FUTURE SCOPE": "chapter_9",
        "Chapter 10: REFERENCES": "chapter_10",
        "Appendix A: CURATED SCHEME CATALOGUE": "appendix_a",
        "Appendix B: TEST AND DEMONSTRATION CHECKLIST": "appendix_b",
    }
    next_id = 100
    for paragraph in document.paragraphs:
        if paragraph.text.strip() in chapter_map:
            add_bookmark(paragraph, chapter_map[paragraph.text.strip()], next_id)
            next_id += 1
    for index, caption in enumerate(figure_captions, start=1):
        match = next((p for p in document.paragraphs if p.text.strip() == caption and "w:drawing" not in p._p.xml), None)
        if match is not None:
            add_bookmark(match, f"figure_{index}", 400 + index)


def format_document(document):
    for section in document.sections:
        # Keep the existing footer and remove any header content.
        for paragraph in section.header.paragraphs:
            paragraph.text = ""
        section.header_distance = Inches(0.15)
        footer = section.footer.paragraphs[0]
        if "PAGE" not in footer._p.xml:
            footer.text = "DCRUST Murthal | "
            add_page_field(footer)

    declaration_or_certificate_labels = {
        "Signature of the Students:",
        "Dev (23001001022)    ______________________________",
        "Devender (23001001023)    ______________________________",
        "Dhruv (23001001024)    ______________________________",
        "Place: DCRUST, Murthal",
        "Date: 2026",
    }
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if paragraph.style.name == "Body Text":
            paragraph.paragraph_format.line_spacing = 1.15
            paragraph.paragraph_format.space_after = Pt(7)
            if text not in declaration_or_certificate_labels and not text.startswith("Project Supervisor"):
                paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif paragraph.style.name.startswith("Heading"):
            paragraph.paragraph_format.keep_with_next = True
        if text.startswith("Figure "):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_before = Pt(2)
            paragraph.paragraph_format.space_after = Pt(8)
            format_runs(paragraph, size=9, color=GRAY)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.line_spacing = 1.05
                    paragraph.paragraph_format.space_after = Pt(3)


def main():
    document = Document(SOURCE)
    set_update_fields(document)
    replace_certificate(document)
    move_cover_logo(document)
    replace_contents_and_add_figures(document)
    format_document(document)
    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
