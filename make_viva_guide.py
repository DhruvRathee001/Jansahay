from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "JanSahay_Viva_Preparation_Guide.docx"
DCRUST_LOGO = ROOT / ".docx_report_work" / "dcrust-source.png"
JANSAHAY_LOGO = ROOT / "frontend" / "jansahay-logo.png"

NAVY = "102A43"
TEAL = "0F766E"
MINT = "DDF4F0"
ORANGE = "F4A36F"
LIGHT = "F5F8FA"
LINE = "D7E3EA"
GRAY = "526A7A"


def shade(cell, color=LIGHT):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), color)


def borders(cell, color=LINE):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_borders = tc_pr.first_child_found_in("w:tcBorders")
    if tc_borders is None:
        tc_borders = OxmlElement("w:tcBorders")
        tc_pr.append(tc_borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = tc_borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            tc_borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), color)


def set_cell_text(cell, text, bold=False, color=NAVY, size=10):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade(cell, NAVY)
        borders(cell)
        set_cell_text(cell, header, bold=True, color="FFFFFF", size=9)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cell = cells[i]
            shade(cell, "FFFFFF" if row_index % 2 == 0 else LIGHT)
            borders(cell)
            set_cell_text(cell, value, size=9)
    if widths:
        for row in table.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.keep_with_next = True
    return p


def add_body(doc, text, bold_lead=None):
    p = doc.add_paragraph(style="Body Text")
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.08
    if bold_lead and text.startswith(bold_lead):
        r = p.add_run(bold_lead)
        r.bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.05
    p.add_run(text)
    return p


def add_number(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(5)
    p.add_run(text)
    return p


def configure(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.75)
    section.header_distance = Inches(0.15)
    section.footer_distance = Inches(0.3)
    section.header.paragraphs[0].text = ""
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.text = "JanSahay | Viva Preparation Guide"
    for run in footer.runs:
        run.font.name = "Arial"
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor.from_string(GRAY)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(NAVY)
    body = doc.styles["Body Text"]
    body.font.name = "Arial"
    body.font.size = Pt(10.5)
    body.font.color.rgb = RGBColor.from_string(NAVY)
    for style_name, size, color in (("Heading 1", 20, NAVY), ("Heading 2", 14, TEAL), ("Heading 3", 11, NAVY)):
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10 if style_name != "Heading 1" else 4)
        style.paragraph_format.space_after = Pt(6)


def add_cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    if DCRUST_LOGO.exists():
        p.add_run().add_picture(str(DCRUST_LOGO), width=Inches(1.2))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("DEENBANDHU CHHOTU RAM UNIVERSITY OF SCIENCE AND TECHNOLOGY, MURTHAL")
    r.bold = True
    r.font.size = Pt(14)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Department of Computer Science and Engineering")
    r.font.size = Pt(12)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(GRAY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(38)
    r = p.add_run("VIVA PREPARATION GUIDE")
    r.bold = True
    r.font.size = Pt(13)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(TEAL)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("JanSahay")
    r.bold = True
    r.font.size = Pt(36)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run("AI-Assisted Personalized Government Service Eligibility and Navigation System")
    r.font.size = Pt(15)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(GRAY)
    if JANSAHAY_LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(JANSAHAY_LOGO), width=Inches(1.0))
    add_table(doc, ["Student", "Roll number"], [
        ["Dev", "23001001022"],
        ["Devender", "23001001023"],
        ["Dhruv", "23001001024"],
    ], widths=[3.2, 2.0])
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Project Supervisor: Dr. Dinesh Singh\nAcademic Year: 2026")
    r.font.size = Pt(11)
    r.font.name = "Arial"
    r.font.color.rgb = RGBColor.from_string(GRAY)
    doc.add_page_break()


def add_contents(doc):
    add_heading(doc, "How to use this guide", 1)
    add_body(doc, "Use this document as a speaking guide rather than reading it word for word. Each member should explain his assigned module, show one working screen or API result, and clearly state the project boundary: JanSahay guides citizens but does not approve benefits or submit government applications.")
    add_table(doc, ["Part", "Presenter", "Main topics"], [
        ["Backend", "Devender", "FastAPI, SQLAlchemy, SQLite, JWT, rule APIs, administrator protection and scheme CRUD"],
        ["Frontend", "Dhruv", "HTML/CSS/JavaScript screens, profile, filters, themes, grouped results and admin workspace"],
        ["Integration and OCR", "Dev", "Natural-language retrieval, Tesseract/PDF extraction, field application, testing and limitations"],
    ], widths=[1.2, 1.5, 3.7])
    add_heading(doc, "One-minute project introduction", 1)
    add_body(doc, "JanSahay is a web-based citizen-support system for discovering government schemes and understanding likely eligibility. A citizen creates a profile, searches in English or Hinglish, filters Central Government and Haryana Government schemes, checks conditions, uploads documents, and follows the official next step. The system uses AI-assisted retrieval for finding relevant schemes, but keeps final eligibility reasoning deterministic and explainable through stored rules.")
    add_heading(doc, "Project facts to remember", 2)
    for item in [
        "45 curated schemes across agriculture, education, healthcare, housing, employment, financial assistance, and social security.",
        "Eligibility statuses: Eligible, Potentially Eligible, and Not Eligible.",
        "Central Government and Haryana Government results are separated throughout the user experience.",
        "SQLite and SQLAlchemy are used for the local prototype; the database can be changed later through the database configuration.",
        "The prototype includes authentication, document upload, OCR support, administrator metrics, and a role-protected scheme management workspace.",
    ]:
        add_bullet(doc, item)


def add_role_sections(doc):
    add_heading(doc, "Part 1 Backend: Devender", 1)
    add_body(doc, "Devender should explain how the server receives requests, checks authentication, loads the database, evaluates rules, and returns structured JSON to the browser.")
    add_heading(doc, "Key backend points", 2)
    for item in [
        "FastAPI defines REST routes for authentication, profiles, schemes, recommendations, eligibility checks, documents, dashboard data, and admin operations.",
        "SQLAlchemy models represent User, CitizenProfile, Scheme, EligibilityCheck, and Document entities.",
        "SQLite keeps the setup simple for a final-year prototype while SQLAlchemy keeps database access portable.",
        "PBKDF2-SHA256 password hashing and JWT access tokens protect authenticated routes.",
        "The require_admin dependency rejects non-admin users from administrator routes with HTTP 403.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "Backend endpoints to demonstrate", 2)
    add_table(doc, ["Route", "Purpose"], [
        ["POST /api/auth/login", "Returns a JWT after password verification."],
        ["GET /api/schemes", "Returns filtered and eligibility-enriched scheme data."],
        ["POST /api/eligibility/check/{scheme_id}", "Evaluates stored rules and records the result."],
        ["GET /api/admin/users", "Shows registered accounts and activity counts to admins."],
        ["POST /api/admin/schemes", "Creates a new catalogue record for an admin."],
        ["PUT /api/admin/schemes/{scheme_id}", "Edits a scheme or restores a deactivated record."],
        ["DELETE /api/admin/schemes/{scheme_id}", "Soft-deactivates a scheme while preserving old checks."],
    ], widths=[2.8, 3.6])
    add_heading(doc, "Likely backend question", 2)
    add_body(doc, "Question: Why is soft-delete used for schemes? Answer: It hides an outdated scheme from citizens but preserves historical eligibility checks and audit context. This is safer than physically deleting a record that may be referenced by earlier activity.")

    add_heading(doc, "Part 2 Frontend: Dhruv", 1)
    add_body(doc, "Dhruv should demonstrate the browser journey and show how a profile change immediately affects the dashboard and catalogue results.")
    add_heading(doc, "Frontend points to show", 2)
    for item in [
        "The interface is built with semantic HTML, responsive CSS, and vanilla JavaScript.",
        "The app stores the JWT in local storage for the local prototype and attaches it to fetch requests.",
        "Scheme filters support search, Central/Haryana government, eligibility status, category, and sorting.",
        "Dashboard and recommendations display Central Government and Haryana Government results separately.",
        "Profile fields include age, state, district, income, occupation, education, family details, land, disability, bank account, Family ID, and document readiness.",
        "The admin view is visible only when the logged-in user has role admin.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "Frontend demonstration order", 2)
    for item in [
        "Sign in with the citizen demo account and show the Overview page.",
        "Open My profile and change one field such as occupation or income.",
        "Open Explore schemes and show government, eligibility, category, and sort filters.",
        "Open a scheme and show the condition explanation and official links.",
        "Switch to the admin account and open Admin insights.",
    ]:
        add_number(doc, item)

    add_heading(doc, "Part 3 Integration and OCR: Dev", 1)
    add_body(doc, "Dev should explain the boundary between AI-assisted search, deterministic eligibility, and document intelligence. This is the most important conceptual part of the project.")
    add_heading(doc, "Integration pipeline", 2)
    add_table(doc, ["Stage", "What happens"], [
        ["Natural-language request", "Tokenization and synonym expansion identify relevant scheme words in English or Hinglish."],
        ["Recommendation", "Scheme text overlap, category relevance, and eligibility result contribute to ranking."],
        ["Eligibility", "JSON rules compare profile values and classify conditions as matched, failed, or missing."],
        ["Document upload", "PDF text is extracted where possible; image files are sent to Tesseract OCR."],
        ["Field extraction", "Regular expressions identify fields such as age, income, land, marks, disability, and state."],
        ["Profile application", "Supported extracted fields can be applied to the citizen profile and eligibility can be rerun."],
    ], widths=[1.8, 4.6])
    add_heading(doc, "Important answer", 2)
    add_body(doc, "Question: Is the final eligibility decision made by AI? Answer: No. AI-assisted retrieval helps find relevant schemes, but the final prototype status comes from explicit deterministic rules. This makes the result explainable and easier to audit.")


def add_admin_and_demo(doc):
    add_heading(doc, "Administrator profile and workspace", 1)
    add_body(doc, "The project already includes a seeded administrator profile. The administrator sees a protected workspace after login and can inspect activity without exposing those controls to citizen accounts.")
    add_table(doc, ["Admin capability", "What it shows or changes"], [
        ["Metrics", "Registered users, active users, admin count, active/inactive schemes, eligibility checks, categories, and status totals."],
        ["Users", "Name, email, role, document count, eligibility-check count, and active status."],
        ["Eligibility audit", "Citizen, scheme, status, score, and timestamp for recorded checks."],
        ["Scheme management", "Add, edit, deactivate, and restore catalogue records with rules, documents, URLs, and benefits."],
        ["Access control", "All admin routes require a valid JWT and role=admin."],
    ], widths=[2.0, 4.4])
    add_body(doc, "Demo administrator account: admin@jansahay.in / admin123. Change this password before any real deployment.", bold_lead="Demo administrator account:")
    add_heading(doc, "Viva demonstration flow", 1)
    for item in [
        "Start the API and open http://127.0.0.1:8000.",
        "Sign in with citizen@example.com / demo123 to show the normal user journey.",
        "Open the profile and explain how profile fields feed the rule engine.",
        "Open Explore schemes and show both government-scope and eligibility filters.",
        "Open one scheme and run Check my eligibility to show matched, failed, and missing conditions.",
        "Open My documents and explain PDF extraction, OCR processing, and Apply fields.",
        "Sign out and sign in as admin@jansahay.local / admin123.",
        "Open Admin insights, show users and eligibility statuses, then edit or add a temporary scheme.",
        "Deactivate the temporary scheme and explain why the project uses soft-delete.",
    ]:
        add_number(doc, item)


def add_viva_questions(doc):
    add_heading(doc, "Likely viva questions and ready answers", 1)
    questions = [
        ("What problem does JanSahay solve?", "It reduces the effort of searching multiple welfare portals by combining profile-based discovery, explainable eligibility, required documents, and official next steps in one interface."),
        ("Why did you choose FastAPI?", "FastAPI provides typed request validation, automatic OpenAPI documentation, clean dependency injection, and a lightweight way to build the REST backend."),
        ("Why SQLite and SQLAlchemy?", "SQLite is easy to run locally for a prototype. SQLAlchemy separates the application from raw SQL and makes a future PostgreSQL migration easier."),
        ("What is the role of AI in the project?", "AI-assisted retrieval interprets the citizen query through tokenization and synonym expansion. Deterministic rules still produce the explainable eligibility status."),
        ("How does OCR work?", "The user uploads an image, Tesseract converts it to text, regular expressions extract supported fields, and the interface allows those fields to be applied to the profile."),
        ("What if Tesseract is unavailable?", "The document remains stored and receives an OCR_UNAVAILABLE status with an explanatory message. The user can install Tesseract and retry processing."),
        ("How do you explain eligibility?", "Every rule is classified as matched, failed, or missing. The response includes the condition label, current value, required value, score, and next action."),
        ("How is the admin protected?", "The user receives a JWT after login. Every admin endpoint uses require_admin, which checks the authenticated database user role before allowing access."),
        ("Can citizens edit schemes?", "No. Only the role-protected administrator workspace can add, edit, deactivate, or restore catalogue entries."),
        ("Does the app submit a government application?", "No. It links the citizen to the official source or application portal. It does not claim government approval or submit an application."),
        ("What are the main limitations?", "Rules are curated demonstration data, retrieval is lexical rather than embedding-based, OCR requires a separate Tesseract installation, and the prototype is not a production deployment."),
        ("What would you do next?", "Add reviewed source-change workflows, immutable audit logs, multilingual retrieval, production storage, stronger document validation, and authorized government APIs where available."),
    ]
    for question, answer in questions:
        p = doc.add_paragraph(style="Body Text")
        p.paragraph_format.space_after = Pt(9)
        r = p.add_run("Q. " + question + "\n")
        r.bold = True
        r.font.color.rgb = RGBColor.from_string(TEAL)
        p.add_run("A. " + answer)


def add_checklist(doc):
    add_heading(doc, "Final preparation checklist", 1)
    for item in [
        "Each member can explain his own module without reading from the screen.",
        "The three members use the same terms: profile, scheme catalogue, rule engine, OCR, and official application channel.",
        "The citizen demo account works before the presentation.",
        "The admin account works and the administrator page shows users, statuses, and scheme management.",
        "Tesseract is installed and its path is configured if a live OCR demonstration is planned.",
        "No real Aadhaar, PAN, bank, or other sensitive identity document is used during the classroom demo.",
        "The team can clearly state what is implemented now and what remains future scope.",
    ]:
        add_bullet(doc, item)
    add_heading(doc, "Run commands", 2)
    p = doc.add_paragraph(style="Body Text")
    p.paragraph_format.left_indent = Inches(0.2)
    r = p.add_run(".\\run.ps1\n# or\n.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload")
    r.font.name = "Consolas"
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    add_body(doc, "Open http://127.0.0.1:8000 after the server starts. The OpenAPI explorer is available at http://127.0.0.1:8000/docs.")


def build():
    doc = Document()
    configure(doc)
    add_cover(doc)
    add_contents(doc)
    add_role_sections(doc)
    add_admin_and_demo(doc)
    add_viva_questions(doc)
    add_checklist(doc)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
