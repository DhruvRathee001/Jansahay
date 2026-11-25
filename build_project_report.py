from collections import Counter
from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from app.scheme_data import SCHEMES


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "JanSahay_Project_Report_Complete.docx"
DCRUST_LOGO = ROOT / ".docx_report_work" / "dcrust-source.png"
JANSAHAY_LOGO = ROOT / "frontend" / "jansahay-logo.png"
SCREENSHOTS = {
    "index_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003533.png"),
    "app_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003344.png"),
    "scheme_data_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003318.png"),
    "security_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003252.png"),
    "schemas_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003227.png"),
    "models_code": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 003158.png"),
    "profile_checklist": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004348.png"),
    "profile_education": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004339.png"),
    "profile": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004331.png"),
    "schemes": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004318.png"),
    "scheme_filter": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004256.png"),
    "dashboard": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004212.png"),
    "document_dropdown": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004202.png"),
    "documents": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004145.png"),
    "login": Path(r"C:\Users\dhruv\OneDrive\Pictures\Screenshots\Screenshot 2026-11-19 004101.png"),
}

TEAM = [
    ("Dev", "23001001022"),
    ("Devender", "23001001023"),
    ("Dhruv", "23001001024"),
]
SUPERVISOR = "Dr. Dinesh Singh"

NAVY = "102A43"
BLUE = "1F4E79"
PALE_BLUE = "EAF2F8"
LIGHT_GRAY = "D9D9D9"
PALE_GRAY = "F5F7F9"
BLACK = RGBColor(0, 0, 0)


def set_run_font(run, name="Cambria", size=11, bold=None, italic=None, color=BLACK):
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def set_style_font(style, name="Cambria", size=11, bold=None, color=BLACK):
    style.font.name = name
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    style.font.size = Pt(size)
    style.font.color.rgb = color
    if bold is not None:
        style.font.bold = bold


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color=LIGHT_GRAY, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn("w:" + margin))
        if node is None:
            node = OxmlElement("w:" + margin)
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def no_table_borders(table):
    for row in table.rows:
        for cell in row.cells:
            set_cell_border(cell, color="FFFFFF", size="0")


def add_page_field(paragraph):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_run_font(run, size=9, color=RGBColor(90, 90, 90))


def add_hyperlink_field(paragraph, text, url):
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), url)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    r_pr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)
    run.append(r_pr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_body(doc, text, style="Body Text", bold_lead=None):
    p = doc.add_paragraph(style=style)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        r = p.add_run(bold_lead)
        set_run_font(r, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2)
    else:
        r = p.add_run(text)
        set_run_font(r)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Paragraph")
    p.paragraph_format.left_indent = Inches(0.25 + 0.22 * level)
    p.paragraph_format.first_line_indent = Inches(-0.15)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.08
    r = p.add_run("- " + text)
    set_run_font(r, size=10.5)
    return p


def add_number(doc, text, number):
    p = doc.add_paragraph(style="List Paragraph")
    p.paragraph_format.left_indent = Inches(0.32)
    p.paragraph_format.first_line_indent = Inches(-0.2)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{number}. {text}")
    set_run_font(r, size=10.5)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    if level == 1:
        p.paragraph_format.page_break_before = True
    r = p.add_run(text)
    set_run_font(r, size={1: 16, 2: 13.5, 3: 12}[level], bold=True, color=BLACK)
    return p


def add_table(doc, headers, rows, widths=None, font_size=9.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = True
    hdr = table.rows[0]
    hdr._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for i, value in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = ""
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, BLUE)
        set_cell_margins(cell, top=120, bottom=120, start=120, end=120)
        set_cell_border(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(value))
        set_run_font(r, size=font_size, bold=True, color=RGBColor(255, 255, 255))
    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cell = cells[i]
            cell.text = ""
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            set_cell_border(cell)
            if ridx % 2 == 1:
                set_cell_shading(cell, PALE_GRAY)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            set_run_font(r, size=font_size, color=BLACK)
    if widths:
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_code(doc, code):
    p = doc.add_paragraph(style="Code Block")
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.right_indent = Inches(0.22)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    for index, line in enumerate(code.strip("\n").splitlines()):
        r = p.add_run(line)
        set_run_font(r, name="Consolas", size=8.3, color=RGBColor(40, 40, 40))
        if index < len(code.strip("\n").splitlines()) - 1:
            r.add_break()
    return p


def add_screenshot(doc, path, caption, width=6.1):
    if not path.exists():
        add_body(doc, f"Screenshot unavailable: {path.name}")
        return
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(4)
    r = cap.add_run(caption)
    set_run_font(r, size=9, italic=True, color=RGBColor(90, 90, 90))


def configure_document(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.75)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

    styles = doc.styles
    set_style_font(styles["Normal"], size=11)
    styles["Normal"].paragraph_format.space_after = Pt(6)
    styles["Normal"].paragraph_format.line_spacing = 1.12
    set_style_font(styles["Body Text"], size=11)
    styles["Body Text"].paragraph_format.space_after = Pt(6)
    styles["Body Text"].paragraph_format.line_spacing = 1.12
    set_style_font(styles["List Paragraph"], size=10.5)
    for level, size in [(1, 16), (2, 13.5), (3, 12)]:
        style = styles[f"Heading {level}"]
        set_style_font(style, size=size, bold=True)
        style.paragraph_format.space_before = Pt(14 if level == 1 else 9)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
    if "Code Block" not in [s.name for s in styles]:
        code_style = styles.add_style("Code Block", WD_STYLE_TYPE.PARAGRAPH)
    else:
        code_style = styles["Code Block"]
    set_style_font(code_style, name="Consolas", size=8.3, color=RGBColor(40, 40, 40))
    code_style.paragraph_format.line_spacing = 1.0

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.paragraph_format.space_after = Pt(0)
    rh = header.add_run("JanSahay | Project Report")
    set_run_font(rh, size=8.5, color=RGBColor(90, 90, 90))

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.paragraph_format.space_before = Pt(0)
    footer.paragraph_format.tab_stops.add_tab_stop(Inches(6.7), WD_TAB_ALIGNMENT.RIGHT)
    rf = footer.add_run("DCRUST Murthal | ")
    set_run_font(rf, size=8.5, color=RGBColor(90, 90, 90))
    add_page_field(footer)

    core = doc.core_properties
    core.title = "JanSahay Project Report"
    core.subject = "AI-assisted personalized government service eligibility and navigation system"
    core.author = "Dev, Devender and Dhruv"
    core.keywords = "JanSahay, government schemes, eligibility, OCR, FastAPI"


def add_cover(doc):
    for _ in range(2):
        doc.add_paragraph()
    if DCRUST_LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(DCRUST_LOGO), width=Inches(1.25))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("DEENBANDHU CHHOTU RAM UNIVERSITY OF SCIENCE AND TECHNOLOGY, MURTHAL")
    set_run_font(r, size=13, bold=True, color=BLACK)
    p.paragraph_format.space_before = Pt(15)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Department of Computer Science and Engineering")
    set_run_font(r, size=12, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(22)
    r = p.add_run("PROJECT REPORT ON")
    set_run_font(r, size=12, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("JanSahay")
    set_run_font(r, size=25, bold=True, color=RGBColor(31, 78, 121))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("An AI-Assisted Personalized Government Service Eligibility and Navigation System")
    set_run_font(r, size=12, italic=True)
    p.paragraph_format.space_after = Pt(22)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Submitted in partial fulfillment of the requirements for the award of the degree of")
    set_run_font(r, size=10.5)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BACHELOR OF TECHNOLOGY IN COMPUTER SCIENCE AND ENGINEERING")
    set_run_font(r, size=12, bold=True)
    doc.add_paragraph()
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(2.4)
    table.columns[1].width = Inches(3.2)
    table.cell(0, 0).text = "Project Supervisor:\n" + SUPERVISOR
    table.cell(0, 1).text = "Submitted By:\n" + "\n".join(f"{name} ({roll})" for name, roll in TEAM)
    no_table_borders(table)
    for cell in table.rows[0].cells:
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                set_run_font(run, size=10.5, bold=True)
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("2026")
    set_run_font(r, size=11, bold=True)
    doc.add_page_break()


def add_declaration(doc):
    add_heading(doc, "DECLARATION", 1)
    add_body(doc, "We hereby declare that the project entitled \"JanSahay: An AI-Assisted Personalized Government Service Eligibility and Navigation System\", submitted in partial fulfillment of the requirements for the award of the Bachelor of Technology degree in Computer Science and Engineering, is our original work. The system was developed by us under the guidance of Dr. Dinesh Singh.")
    add_body(doc, "The project combines a curated knowledge base of Central Government and Haryana Government schemes, a deterministic eligibility engine, natural-language recommendation, document upload and OCR support, and an official-source navigation workflow. Wherever external documentation, libraries, or government sources have been used, they have been acknowledged in the references.")
    doc.add_paragraph()
    add_body(doc, "Signature of the Students:")
    for name, roll in TEAM:
        add_body(doc, f"{name} ({roll})    ______________________________")
    add_body(doc, "Place: DCRUST, Murthal\nDate: 2026")


def add_certificate(doc):
    add_heading(doc, "CERTIFICATE", 1)
    add_body(doc, "This is to certify that the project report entitled \"JanSahay: An AI-Assisted Personalized Government Service Eligibility and Navigation System\" has been prepared and submitted by Dev (23001001022), Devender (23001001023), and Dhruv (23001001024) of the Department of Computer Science and Engineering, Deenbandhu Chhotu Ram University of Science and Technology, Murthal, under my guidance and supervision.")
    add_body(doc, "The work presented in this report is suitable for consideration as a final-year project report, subject to the rules and evaluation requirements of the University.")
    doc.add_paragraph("\n\n")
    add_body(doc, f"Project Supervisor: {SUPERVISOR}")
    add_body(doc, "Signature: ______________________________")
    doc.add_paragraph()
    add_body(doc, "Head of Department: ______________________________")
    add_body(doc, "External Examiner: ______________________________")


def add_front_matter(doc):
    add_heading(doc, "ABSTRACT", 1)
    add_body(doc, "Citizens often find it difficult to identify government schemes that match their age, income, occupation, location, education, family circumstances, and available documents. JanSahay is a web-based citizen-support prototype that brings relevant Central Government and Haryana Government schemes into one guided interface. It combines a curated catalogue of 45 schemes, a citizen profile, natural-language scheme discovery, a deterministic rule engine, document intelligence, and an official application navigator.")
    add_body(doc, "The recommendation layer uses token matching and synonym expansion to retrieve schemes from English and Hinglish-oriented requests. The eligibility layer applies explicit JSON-based conditions and returns Eligible, Potentially Eligible, or Not Eligible results with matched conditions, failed conditions, and missing information. Documents can be uploaded, processed with PDF extraction or Tesseract OCR, and used to populate selected profile fields. JanSahay does not approve benefits or submit government applications; it explains likely eligibility and directs citizens to official channels.")
    add_body(doc, "The implemented prototype uses Python, FastAPI, SQLAlchemy, SQLite, HTML, CSS, vanilla JavaScript, JWT authentication, Tesseract OCR, Docker, and Pytest. Testing covers health checks, seeded catalogue integrity, eligibility rules, conflict handling, OCR field extraction, scope separation, and recommendation grouping.")

    add_heading(doc, "ACKNOWLEDGEMENTS", 1)
    add_body(doc, "We express our sincere gratitude to our project supervisor, Dr. Dinesh Singh, Department of Computer Science and Engineering, for his guidance, feedback, and encouragement throughout the development of JanSahay.")
    add_body(doc, "We are thankful to the Department of Computer Science and Engineering and Deenbandhu Chhotu Ram University of Science and Technology, Murthal, for providing the academic environment and resources required to complete this project. We also acknowledge the official Central Government and Haryana Government scheme portals that informed the curated catalogue and application links.")
    add_body(doc, "Finally, we thank our families, friends, and classmates for their support during requirement analysis, implementation, testing, and documentation.")

    add_heading(doc, "TABLE OF CONTENTS", 1)
    contents = [
        "Chapter 1: Introduction",
        "Chapter 2: System Analysis and Design",
        "Chapter 3: Hardware and Software Specification",
        "Chapter 4: Tools and Technologies Used",
        "Chapter 5: Control Flow of JanSahay",
        "Chapter 6: Source Code",
        "Chapter 7: Project Output",
        "Chapter 8: Functioning of the Application",
        "Chapter 9: Conclusion and Future Scope",
        "Chapter 10: References",
        "Appendix A: Curated Scheme Catalogue",
        "Appendix B: Test and Demonstration Checklist",
    ]
    for item in contents:
        add_bullet(doc, item)


def chapter_one(doc):
    add_heading(doc, "Chapter 1: INTRODUCTION", 1)
    add_heading(doc, "1.1 Project Overview", 2)
    add_body(doc, "Government welfare schemes provide support in education, agriculture, healthcare, housing, employment, financial assistance, and social security. However, citizens frequently have to search several departmental websites, understand lengthy eligibility conditions, and determine which documents are required. The problem is especially difficult when a scheme depends on multiple facts such as income, land ownership, age, state, education, family details, or existing benefits.")
    add_body(doc, "JanSahay is proposed as a web-based, AI-assisted government-service eligibility and navigation system. A citizen creates a profile, asks a natural-language question, explores schemes, checks eligibility, uploads documents, and follows official application steps. The system focuses on explanation and discovery rather than unauthorized application submission.")
    if JANSAHAY_LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.add_run().add_picture(str(JANSAHAY_LOGO), width=Inches(1.25))
        caption = doc.add_paragraph()
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = caption.add_run("Figure 1.1 JanSahay identity mark")
        set_run_font(r, size=9, italic=True, color=RGBColor(90, 90, 90))
    add_heading(doc, "1.2 Motivation", 2)
    add_body(doc, "The motivation for JanSahay is to reduce information overload and make scheme discovery understandable for ordinary citizens. A single profile allows the same information to be evaluated across multiple schemes. The interface presents the reason for a result, identifies missing information, separates Central Government and Haryana Government schemes, and links each scheme to its official source or application portal.")
    add_heading(doc, "1.3 Problem Statement", 2)
    add_body(doc, "Citizens face the following recurring problems while seeking public benefits:")
    for item in [
        "No unified view of relevant schemes across departments and government levels.",
        "Difficulty interpreting eligibility rules written in lengthy or technical language.",
        "Lack of personalized recommendations based on the citizen's complete profile.",
        "Unclear reasons for eligibility, ineligibility, or missing information.",
        "Repeated effort in preparing, locating, and reusing supporting documents.",
        "No clear path from scheme discovery to the official application channel.",
        "Limited visibility into scheme coverage and common eligibility gaps.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.4 Objectives", 2)
    for item in [
        "Design and develop a secure web application for personalized government-service discovery.",
        "Create a structured catalogue of 45 Central Government and Haryana Government schemes.",
        "Implement an eligibility engine with Eligible, Potentially Eligible, and Not Eligible statuses.",
        "Explain each result through matched conditions, failed conditions, and missing information.",
        "Use natural-language retrieval to understand English and Hinglish-oriented requests.",
        "Provide document upload, PDF/image text extraction, OCR, and basic field extraction.",
        "Guide citizens through required documents and official application steps.",
        "Provide an administrator view of catalogue coverage and eligibility activity.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "1.5 Scope and Boundaries", 2)
    add_body(doc, "The initial scope covers a curated set of Central Government and Haryana Government schemes. The platform supports citizen profiles, scheme search, natural-language discovery, rule-based eligibility assessment, document management, official source links, a dark theme, government-scope filtering, and basic administrator metrics.")
    add_body(doc, "JanSahay is a local academic prototype. It does not claim to cover every Indian scheme, provide automatic government approval, make legal or medical decisions, or submit applications without an authorized integration. Scheme rules and thresholds must be reviewed against current official notifications before production use.")
    add_heading(doc, "1.6 Feasibility Study", 2)
    add_heading(doc, "Economic Feasibility", 3)
    add_body(doc, "The project is economically feasible because it uses open-source technologies and a local SQLite database. The prototype can run on an ordinary development computer without paid cloud services. Future production deployment would require managed storage, secure backups, monitoring, and operational support.")
    add_heading(doc, "Technical Feasibility", 3)
    add_body(doc, "The application is technically feasible because FastAPI provides a lightweight REST API, SQLAlchemy provides database access, SQLite is adequate for demonstration, and the browser interface requires no frontend build system. Tesseract OCR is used as a local document-processing dependency. Docker support provides a repeatable deployment path.")
    add_heading(doc, "Operational Feasibility", 3)
    add_body(doc, "The workflow is suitable for a citizen-support demonstration: a user can register, complete a profile, search schemes, view explanations, process documents, and open official links. The interface is responsive and includes readable statuses and next actions. A production rollout would require accessibility testing, multilingual review, staff training, and official data governance.")


def chapter_two(doc):
    add_heading(doc, "Chapter 2: SYSTEM ANALYSIS AND DESIGN", 1)
    add_heading(doc, "2.1 Existing System", 2)
    add_body(doc, "Existing scheme discovery is commonly distributed across department portals, PDF notifications, static pages, and help-desk interactions. A citizen must often repeat the same profile information and manually compare conditions. Generic search returns broad results but does not reliably connect the request with age, income, occupation, location, family situation, and required documents.")
    add_heading(doc, "2.2 Proposed System", 2)
    add_body(doc, "The proposed system maintains a structured scheme knowledge base and connects it to a citizen profile and explanation engine. Natural-language requests are used for relevance ranking. The explicit rule engine remains responsible for the eligibility status. The application navigator presents required documents, ordered steps, official information links, and application portals where available.")
    add_heading(doc, "2.3 User Roles", 2)
    add_table(doc, ["Role", "Responsibilities", "Implemented Access"], [
        ["Citizen", "Register, maintain profile, search schemes, check eligibility, upload documents, apply extracted fields, open official links.", "JWT-authenticated citizen routes"],
        ["Administrator", "View catalogue coverage, user count, scheme count, and eligibility activity.", "Admin-only metrics endpoint"],
        ["System", "Seed schemes, evaluate rules, rank recommendations, process documents, and maintain database records.", "FastAPI service and SQLAlchemy models"],
    ], widths=[1.1, 3.5, 1.7], font_size=9)
    add_heading(doc, "2.4 Functional Requirements", 2)
    for item in [
        "Users shall register and log in using email and password.",
        "The system shall store personal, family, economic, education, residence, land, and benefit information.",
        "The system shall list the curated scheme catalogue and support search, category, government-scope, eligibility, and sort filters.",
        "The system shall evaluate profile conditions and provide a transparent explanation.",
        "The system shall accept PDF, image, and text document uploads.",
        "The system shall extract selected fields and allow the user to apply them to the profile.",
        "The system shall show official information and application portal links.",
        "The system shall provide basic administrator metrics.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "2.5 Non-functional Requirements", 2)
    add_table(doc, ["Requirement", "Design Response"], [
        ["Usability", "Plain-language labels, explanation statuses, responsive layout, and separate Central/Haryana results."],
        ["Security", "JWT authentication, password hashing, user-scoped documents, and protected admin metrics."],
        ["Maintainability", "Separate models, schemas, rule engine, recommendation module, seed data, and frontend modules."],
        ["Reliability", "Validated API inputs, database transactions, duplicate-upload protection, and test coverage."],
        ["Portability", "SQLite default, environment-based configuration, and Docker support."],
    ], widths=[1.4, 4.9], font_size=9.5)
    add_heading(doc, "2.6 System Architecture", 2)
    add_body(doc, "JanSahay follows a layered architecture. The browser presents views and sends REST requests. FastAPI handles authentication, profile operations, recommendations, eligibility checks, document workflow, and admin metrics. SQLAlchemy maps application entities to SQLite. The rule engine evaluates explicit JSON conditions, while the recommendation module ranks schemes using token overlap, synonyms, category relevance, and eligibility signals.")
    add_table(doc, ["Layer", "Components", "Purpose"], [
        ["Presentation", "HTML, CSS, vanilla JavaScript", "Login, dashboard, scheme catalogue, profile, document library, modal explanations."],
        ["API", "FastAPI, Pydantic, JWT", "Validated REST routes, authentication, authorization, and response serialization."],
        ["Business logic", "Rules and recommendation modules", "Eligibility evaluation, conflict checks, relevance ranking, and explanations."],
        ["Data", "SQLAlchemy and SQLite", "Profiles, users, schemes, documents, and eligibility checks."],
        ["Document intelligence", "pypdf, Pillow, pytesseract", "PDF text extraction, image OCR, and basic field extraction."],
    ], widths=[1.2, 2.4, 2.7], font_size=9)
    add_heading(doc, "2.7 Data Model", 2)
    add_table(doc, ["Entity", "Important Attributes", "Relationship or Purpose"], [
        ["User", "id, name, email, password hash, role", "Owns a citizen profile and documents."],
        ["CitizenProfile", "age, state, income, occupation, education, family, land, benefits", "Input used by the rule engine."],
        ["Scheme", "name, department, category, scope, benefits, rules, documents, URLs", "Curated knowledge-base record."],
        ["Document", "type, file path, extracted text, fields, validation status", "Proof record linked to a citizen."],
        ["EligibilityCheck", "scheme, status, score, matched, failed, missing", "Audit record for a rule evaluation."],
    ], widths=[1.35, 2.7, 2.25], font_size=9)
    add_heading(doc, "2.8 Main Control Flow", 2)
    for n, item in enumerate([
        "The citizen registers or logs in and receives a JWT access token.",
        "The citizen completes the profile or applies fields extracted from documents.",
        "The dashboard evaluates active schemes against the current profile.",
        "A natural-language request is tokenized, expanded with synonyms, and ranked against scheme text.",
        "The citizen opens a scheme and can run a detailed eligibility check.",
        "The system presents conditions, missing information, required documents, and official next steps.",
    ], 1):
        add_number(doc, item, n)


def chapter_three(doc):
    add_heading(doc, "Chapter 3: HARDWARE AND SOFTWARE SPECIFICATION", 1)
    add_heading(doc, "3.1 Hardware Requirements", 2)
    add_table(doc, ["Component", "Minimum Demonstration Requirement", "Recommended"], [
        ["Processor", "Dual-core CPU", "Intel Core i5 or equivalent"],
        ["Memory", "4 GB RAM", "8 GB RAM"],
        ["Storage", "2 GB free project space", "10 GB free space including OCR tools and uploads"],
        ["Display", "1366 x 768", "Full HD display"],
        ["Network", "Localhost access", "Stable internet for official links and package installation"],
    ], widths=[1.5, 2.3, 2.5], font_size=9.5)
    add_heading(doc, "3.2 Software Requirements", 2)
    add_table(doc, ["Software", "Version or Role"], [
        ["Windows, Linux, or macOS", "Operating system for local development"],
        ["Python", "3.11 or later"],
        ["FastAPI and Uvicorn", "REST API and local ASGI server"],
        ["SQLAlchemy and SQLite", "ORM and default relational database"],
        ["Pydantic", "Request and response validation"],
        ["Pillow and pytesseract", "Image handling and OCR bridge"],
        ["Tesseract OCR", "External OCR executable for image documents"],
        ["Browser", "Chrome, Edge, Firefox, or equivalent modern browser"],
        ["Docker", "Optional containerized deployment"],
        ["Pytest and HTTPX", "Automated testing"],
    ], widths=[2.1, 4.2], font_size=9.5)
    add_heading(doc, "3.3 Installation and Execution", 2)
    add_number(doc, "Open PowerShell in the JanSahay project folder.", 1)
    add_number(doc, "Create or activate the virtual environment.", 2)
    add_number(doc, "Install the Python dependencies with .venv\\Scripts\\python.exe -m pip install -r requirements.txt.", 3)
    add_number(doc, "Install Tesseract OCR for image document processing and set TESSERACT_CMD if it is not on PATH.", 4)
    add_number(doc, "Run .\\run.ps1 and open http://127.0.0.1:8000.", 5)


def chapter_four(doc):
    add_heading(doc, "Chapter 4: TOOLS AND TECHNOLOGIES USED", 1)
    sections = [
        ("4.1 Python and FastAPI", "Python is used for the backend because it has mature libraries for API development, validation, databases, OCR, and testing. FastAPI exposes documented REST routes and supports dependency injection for database sessions and authenticated users."),
        ("4.2 SQLAlchemy and SQLite", "SQLAlchemy defines the User, CitizenProfile, Scheme, Document, and EligibilityCheck models. SQLite is used as the default database for simple local deployment and demonstration. The database bootstrap process creates missing columns and seeds the catalogue."),
        ("4.3 HTML, CSS, and JavaScript", "The frontend is implemented with browser-native HTML, CSS, and JavaScript. It provides views for authentication, overview, schemes, documents, profile, and administration. The responsive visual system includes a light theme and a dark theme."),
        ("4.4 Authentication and Security", "JWT tokens protect authenticated API routes. Passwords are stored as hashes. Document queries are scoped to the current user, and administrator metrics require the administrator role. The project is a local prototype and requires HTTPS, secret rotation, and stronger deployment controls in production."),
        ("4.5 Eligibility Rule Engine", "The rule engine evaluates operators such as equality, ranges, minimum values, and boolean conditions. It records matched conditions, failed conditions, missing information, and a score. Conflict rules can prevent incompatible Haryana benefits from being simultaneously treated as eligible."),
        ("4.6 Natural-language Retrieval", "The current implementation uses tokenization, stop-word removal, synonym expansion, category bonuses, and eligibility bonuses. It is transparent and easy to demonstrate. It is a lexical retrieval system rather than a transformer-embedding or large-language-model system."),
        ("4.7 Document Intelligence", "Text files and PDFs are extracted directly where possible. Images are processed through Tesseract OCR. Regular expressions identify fields such as income, land area, date of birth, age, disability percentage, marks percentage, and state. The user reviews and applies selected fields rather than receiving an automatic government decision."),
        ("4.8 Docker and Testing", "Docker packages the service and includes the Tesseract dependency in the Linux image. Pytest covers seeded data, eligibility outcomes, conflict handling, OCR field extraction, scope filtering, grouped results, and recommendation output."),
    ]
    for title, body in sections:
        add_heading(doc, title, 2)
        add_body(doc, body)
    add_heading(doc, "4.9 Catalogue Coverage", 2)
    counts = Counter((s["scope"], s["category"]) for s in SCHEMES)
    rows = []
    for scope in ("Central Government", "Haryana Government"):
        for category in sorted({s["category"] for s in SCHEMES}):
            if counts[(scope, category)]:
                rows.append([scope, category, counts[(scope, category)]])
    add_table(doc, ["Government Scope", "Category", "Scheme Count"], rows, widths=[2.0, 2.6, 1.2], font_size=9)


def chapter_five(doc):
    add_heading(doc, "Chapter 5: CONTROL FLOW OF JANSAHAY", 1)
    flows = [
        ("5.1 Authentication and Session", "A user submits email and password to the login route. The API verifies the password, returns a JWT, and the browser stores the token locally for subsequent API calls. The client loads the user, dashboard, profile, schemes, and documents after authentication."),
        ("5.2 Profile Completion", "The citizen enters age, state, district, income, occupation, education, family, land, disability, residence, and benefit information. Saving the profile triggers a fresh dashboard and scheme catalogue evaluation."),
        ("5.3 Natural-language Recommendation", "A request such as a farmer asking for financial support is tokenized. Synonym groups expand terms such as farmer, agriculture, kisan, and kheti. Scheme text is scored for overlap and category relevance. Eligibility results from the same profile add a ranking signal. Results are shown separately for Central Government and Haryana Government schemes."),
        ("5.4 Eligibility Assessment", "When the user opens a scheme, the system evaluates its JSON rules. Every condition is classified as matched, failed, or missing. The response includes the status, percentage score, explanation, and next action."),
        ("5.5 Document Workflow", "The user selects a document type and uploads a PDF, image, or text file. PDFs and text files are extracted directly; images are sent through Tesseract OCR. Extracted fields are displayed in the document library. The user can apply supported values to the profile and rerun eligibility."),
        ("5.6 Official Application Navigation", "The scheme detail view shows required documents, ordered next steps, official information source, and application portal when available. JanSahay does not simulate or submit a government application."),
        ("5.7 Administrator Metrics", "The administrator view shows the number of users, schemes, eligibility checks, category coverage, and eligibility statuses. This supports demonstration of system activity without exposing citizen details in the dashboard view."),
    ]
    for title, body in flows:
        add_heading(doc, title, 2)
        add_body(doc, body)
    add_heading(doc, "5.8 Request and Response Flow", 2)
    add_table(doc, ["Step", "Actor", "Action", "Output"], [
        ["1", "Citizen", "Logs in", "JWT token"],
        ["2", "Citizen", "Completes profile or uploads proof", "Profile data and document record"],
        ["3", "API", "Loads active schemes", "Scheme catalogue"],
        ["4", "Rule engine", "Evaluates explicit conditions", "Status, score, explanations"],
        ["5", "Recommendation module", "Ranks natural-language matches", "Relevant schemes"],
        ["6", "Frontend", "Groups and displays results", "Actionable citizen guidance"],
    ], widths=[0.55, 1.05, 2.5, 2.2], font_size=9)


def chapter_six(doc):
    add_heading(doc, "Chapter 6: SOURCE CODE", 1)
    add_body(doc, "The complete source code is maintained in the JanSahay project folder. The following excerpts show the main implementation ideas without reproducing every file in the report.")
    add_heading(doc, "6.1 Scheme Catalogue API", 2)
    add_code(doc, '''@app.get("/api/schemes", response_model=list[SchemeOut])
def list_schemes(q=None, category=None, eligibility=None,
                 scope=None, sort="eligibility", user=None, db=None):
    schemes = load_active_schemes(db, scope=scope, category=category)
    return enrich_with_profile_eligibility(schemes, user.profile)''')
    add_screenshot(doc, SCREENSHOTS["app_code"], "Figure 6.1 Frontend API and authentication code")
    add_heading(doc, "6.2 Explainable Rule Evaluation", 2)
    add_code(doc, '''for rule in scheme.rules or []:
    actual = getattr(profile, rule["field"], None)
    if actual is None:
        missing_information.append(rule)
    elif compare(actual, rule["operator"], rule.get("value")):
        matched_conditions.append(rule)
    else:
        failed_conditions.append(rule)''')
    add_screenshot(doc, SCREENSHOTS["scheme_data_code"], "Figure 6.2 Scheme catalogue and rule data")
    add_heading(doc, "6.3 Recommendation Ranking", 2)
    add_code(doc, '''query_tokens = tokenize(query)
expanded = expand_synonyms(query_tokens)
overlap = len(expanded & tokenize(scheme_text))
raw = overlap * 10 + category_bonus * 5 + eligibility_bonus * 4
recommendations.append(rank_and_explain(scheme, raw))''')
    add_screenshot(doc, SCREENSHOTS["index_code"], "Figure 6.3 Frontend application shell and catalogue controls")
    add_heading(doc, "6.4 OCR Field Extraction", 2)
    add_code(doc, '''text = pytesseract.image_to_string(Image.open(path))
fields = extract_fields(text, document_type)
document.extracted_text = text
document.extracted_fields = fields
document.validation_status = "TEXT_EXTRACTED"''')
    add_heading(doc, "6.5 Security, Schemas, and Database Models", 2)
    add_body(doc, "The following source views show password hashing and JWT creation, Pydantic profile fields, and SQLAlchemy entity definitions.")
    add_screenshot(doc, SCREENSHOTS["security_code"], "Figure 6.4 Password hashing and JWT security implementation")
    add_screenshot(doc, SCREENSHOTS["schemas_code"], "Figure 6.5 Profile validation schema")
    add_screenshot(doc, SCREENSHOTS["models_code"], "Figure 6.6 SQLAlchemy data models")
    add_heading(doc, "6.6 Frontend Scope Filtering", 2)
    add_code(doc, '''const filtered = state.schemes.filter((scheme) =>
  (!scope || scheme.scope === scope) &&
  (!eligibility || scheme.eligibility_status === eligibility) &&
  matchesSearch(scheme, query));''')


def chapter_seven(doc):
    add_heading(doc, "Chapter 7: PROJECT OUTPUT", 1)
    add_body(doc, "The completed prototype provides the following user-visible outputs. The interface uses the JanSahay logo, light and dark themes, readable status badges, and responsive layouts for desktop and mobile screens.")
    add_table(doc, ["Screen", "Visible Output", "Purpose"], [
        ["Login and Registration", "Citizen login, registration, demo profile, theme toggle", "Secure entry into the personalized experience"],
        ["Overview", "Profile completeness, scheme totals, eligible and potential counts, grouped matches", "Quick understanding of the citizen's support map"],
        ["Explore Schemes", "Search, Central/Haryana filter, eligibility filter, category filter, sorting", "Find and compare schemes"],
        ["Scheme Details", "Benefits, documents, steps, eligibility check, source and portal links", "Explain what to do next"],
        ["My Documents", "Upload library, OCR status, extracted fields, Process OCR, Apply fields", "Maintain proof readiness"],
        ["My Profile", "Citizen fields, quick flags, document checklist", "Maintain eligibility inputs and document readiness"],
        ["Administrator", "Users, schemes, eligibility checks, categories, statuses", "View basic activity metrics"],
    ], widths=[1.5, 3.0, 1.8], font_size=9)
    add_screenshot(doc, SCREENSHOTS["login"], "Figure 7.1 JanSahay login screen")
    add_screenshot(doc, SCREENSHOTS["dashboard"], "Figure 7.2 Personalized dashboard")
    add_screenshot(doc, SCREENSHOTS["profile"], "Figure 7.3 Citizen profile")
    add_screenshot(doc, SCREENSHOTS["profile_education"], "Figure 7.4 Education and family profile fields")
    add_screenshot(doc, SCREENSHOTS["profile_checklist"], "Figure 7.5 Profile document checklist")
    add_screenshot(doc, SCREENSHOTS["schemes"], "Figure 7.6 Scheme catalogue")
    add_screenshot(doc, SCREENSHOTS["scheme_filter"], "Figure 7.7 Eligibility filtering")
    add_screenshot(doc, SCREENSHOTS["document_dropdown"], "Figure 7.8 Document type selection")
    add_screenshot(doc, SCREENSHOTS["documents"], "Figure 7.9 Uploaded documents and extracted fields")
    add_heading(doc, "7.1 Output Interpretation", 2)
    add_body(doc, "The output is intentionally explanatory. A green Eligible result means that the available profile data satisfies all evaluated conditions. A Potentially Eligible result means that the scheme appears relevant but required profile information is missing. A Not Eligible result identifies the failed conditions. These statuses are guidance generated from the stored prototype rules and are not government approvals.")
    add_heading(doc, "7.2 Government Scope Presentation", 2)
    add_body(doc, "The dashboard and natural-language recommendation results are divided into Central Government and Haryana Government sections. The catalogue also includes a government-scope filter, so a user can view all schemes, only Central schemes, or only Haryana schemes.")


def chapter_eight(doc):
    add_heading(doc, "Chapter 8: FUNCTIONING OF THE APPLICATION", 1)
    add_heading(doc, "8.1 Citizen Demonstration Flow", 2)
    for n, item in enumerate([
        "Start the API with the run script and open the local browser address.",
        "Use the demo profile or create a new citizen account.",
        "Open My profile and enter age, state, income, occupation, education, family, and land details.",
        "Return to Overview to view the first Central Government and Haryana Government matches.",
        "Use the search box or a suggested query to retrieve relevant schemes.",
        "Open a scheme, run Check my eligibility, and review matched, failed, and missing conditions.",
        "Open My documents, upload proof, process OCR where required, and apply extracted fields.",
        "Follow the official source and application portal link shown in the scheme details.",
    ], 1):
        add_number(doc, item, n)
    add_heading(doc, "8.2 Validation and Error Handling", 2)
    for item in [
        "API input schemas enforce field types, lengths, and numeric ranges.",
        "Unsupported file extensions are rejected before storage.",
        "Duplicate document records are prevented for the same user, type, and filename.",
        "Unauthorized users cannot access protected profile, document, or eligibility routes.",
        "A missing OCR dependency produces an explicit OCR_UNAVAILABLE status and a retry option.",
        "A missing profile value is shown as missing information rather than treated as a failed rule.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "8.3 Testing Summary", 2)
    add_table(doc, ["Test Area", "Coverage", "Result"], [
        ["Health and startup", "Health route returns OK; seeded application imports", "Passed"],
        ["Demo user and profile", "Seeded citizen and Haryana profile are available", "Passed"],
        ["Catalogue", "45 schemes and eligibility ordering", "Passed"],
        ["Eligibility", "PM-KISAN eligible case and rule score", "Passed"],
        ["Conflict and OCR fields", "Haryana pension conflict and extracted fields", "Passed"],
        ["Scope and recommendations", "Central/Haryana filtering and grouped results", "Passed"],
    ], widths=[1.6, 3.7, 1.0], font_size=9)
    add_body(doc, "The automated test suite reports 6 passing tests. Manual demonstration should additionally verify a real Tesseract installation with a sample image, official links, browser refresh after frontend changes, and the responsive layout at desktop and mobile widths.")
    add_heading(doc, "8.4 Security and Privacy Considerations", 2)
    add_body(doc, "The application processes potentially sensitive identity and financial documents. The prototype keeps documents in local storage and scopes document access to the owning user. A production deployment would require encryption at rest, secure object storage, HTTPS, secret management, malware scanning, retention controls, access auditing, and a clear privacy notice. Users should not upload real identity documents to an unprotected demonstration deployment.")


def chapter_nine(doc):
    add_heading(doc, "Chapter 9: CONCLUSION AND FUTURE SCOPE", 1)
    add_heading(doc, "9.1 Conclusion", 2)
    add_body(doc, "JanSahay demonstrates how a citizen-support platform can combine structured scheme data, explicit rule reasoning, natural-language retrieval, document intelligence, and official-source navigation. The prototype reduces the effort required to find relevant schemes and makes the reason for each eligibility result visible to the user.")
    add_body(doc, "The project delivers a working local web application with authentication, citizen profiles, a curated 45-scheme catalogue, Central/Haryana separation, eligibility explanations, OCR-assisted document workflow, official links, administrative metrics, Docker configuration, and automated tests. The most important design decision is the separation of AI-assisted retrieval from deterministic eligibility reasoning, which keeps the final explanation auditable.")
    add_heading(doc, "9.2 Current Limitations", 2)
    for item in [
        "Natural-language retrieval is lexical and synonym-based rather than embedding-based semantic search.",
        "The prototype uses SQLite and does not include production database migrations.",
        "The administrator view provides metrics but not full scheme CRUD management.",
        "OCR depends on a separately installed Tesseract executable on Windows.",
        "Rules and thresholds are curated demonstration data and require official review before public use.",
        "The platform guides applications but does not submit them or verify government approval.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "9.3 Future Scope", 2)
    for item in [
        "Add Sentence Transformers with FAISS or pgvector for semantic retrieval and multilingual embeddings.",
        "Add authorized government APIs for application submission and status tracking.",
        "Add source-change detection and administrator review for scheme updates.",
        "Introduce Redis caching and Celery workers for OCR, notifications, and reports.",
        "Add Hindi and other Indian-language interfaces, speech input, and assisted-access modes.",
        "Improve document validation with advanced vision models and fraud checks.",
        "Migrate production deployments to PostgreSQL, object storage, encryption, and audited access control.",
    ]:
        add_bullet(doc, item)


def chapter_ten(doc):
    add_heading(doc, "Chapter 10: REFERENCES", 1)
    refs = [
        ("JanSahay Project Synopsis", "Internal project synopsis, Department of Computer Science and Engineering, DCRUST Murthal."),
        ("MyScheme Portal", "https://www.myscheme.gov.in/"),
        ("National Portal of India", "https://www.india.gov.in/"),
        ("Government of Haryana", "https://haryana.gov.in/"),
        ("FastAPI Documentation", "https://fastapi.tiangolo.com/"),
        ("SQLAlchemy Documentation", "https://www.sqlalchemy.org/"),
        ("Pydantic Documentation", "https://docs.pydantic.dev/"),
        ("Tesseract OCR Documentation", "https://tesseract-ocr.github.io/"),
        ("Pytest Documentation", "https://docs.pytest.org/"),
        ("Docker Documentation", "https://docs.docker.com/"),
        ("Haryana Scholarship Portal", "https://harchhatravratti.highereduhry.ac.in/"),
        ("Haryana Vivah Shagun Information", "https://schemes.haryanascbc.gov.in/Citizen/aboutVivahshagun"),
    ]
    for title, url in refs:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.first_line_indent = Inches(-0.2)
        p.paragraph_format.space_after = Pt(5)
        r = p.add_run(title + ": ")
        set_run_font(r, bold=True, size=10.5)
        add_hyperlink_field(p, url, url)


def appendices(doc):
    add_heading(doc, "Appendix A: CURATED SCHEME CATALOGUE", 1)
    add_body(doc, "The application contains 45 seeded schemes. The catalogue is organized into 28 Central Government entries and 17 Haryana Government entries. The scope labels below are the values used by the application filter and grouped recommendation results.")
    rows = []
    for scheme in SCHEMES:
        rows.append([scheme["code"], scheme["name"], scheme["scope"], scheme["category"]])
    add_table(doc, ["Code", "Scheme", "Scope", "Category"], rows, widths=[1.25, 2.75, 1.35, 1.15], font_size=7.7)
    add_heading(doc, "Appendix B: TEST AND DEMONSTRATION CHECKLIST", 1)
    add_table(doc, ["Check", "Expected Result", "Status"], [
        ["Login with demo account", "Dashboard opens and profile loads", "Verified"],
        ["Search farmer support", "Relevant schemes appear with explanations", "Verified"],
        ["Filter Central Government", "Only Central Government cards remain", "Verified"],
        ["Filter Haryana Government", "Only Haryana Government cards remain", "Verified"],
        ["Open scheme details", "Rules, documents, steps, official links appear", "Verified"],
        ["Upload text/PDF document", "Text extraction and fields appear", "Verified"],
        ["Process image OCR", "Tesseract status and fields appear", "Requires local Tesseract"],
        ["Apply extracted fields", "Profile values update and matches refresh", "Verified in code"],
        ["Run automated tests", "Six tests pass", "Verified"],
    ], widths=[2.0, 3.5, 1.0], font_size=9)


def build():
    doc = Document()
    configure_document(doc)
    add_cover(doc)
    add_declaration(doc)
    add_certificate(doc)
    add_front_matter(doc)
    chapter_one(doc)
    chapter_two(doc)
    chapter_three(doc)
    chapter_four(doc)
    chapter_five(doc)
    chapter_six(doc)
    chapter_seven(doc)
    chapter_eight(doc)
    chapter_nine(doc)
    chapter_ten(doc)
    appendices(doc)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
