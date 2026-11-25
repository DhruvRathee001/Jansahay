from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
TMP = ROOT / "tmp" / "pdfs"
OUTPUT = ROOT / "JanSahay_Project_Synopsis.pdf"
REFERENCE_RENDER = TMP / "reference-cover-300.png"
LOGO_CROP = TMP / "university-logo.png"

BLUE = colors.HexColor("#1F3E73")
TABLE_BLUE = colors.HexColor("#D8E2F2")
TEXT = colors.HexColor("#111111")


def make_logo():
    TMP.mkdir(parents=True, exist_ok=True)
    if not REFERENCE_RENDER.exists():
        return None
    image = Image.open(REFERENCE_RENDER).convert("RGB")
    # The crop contains the university emblem from the supplied reference cover.
    crop = image.crop((850, 520, 1700, 1390))
    crop.save(LOGO_CROP, quality=95)
    return LOGO_CROP


def paragraph(text, style):
    return Paragraph(text, style)


def bullets(items, style):
    return [
        Paragraph(f"- {item}", style)
        for item in items
    ]


def make_table(data, widths, styles):
    formatted = []
    for row_index, row in enumerate(data):
        formatted.append(
            [
                Paragraph(str(cell), styles["table_header"] if row_index == 0 else styles["table"])
                for cell in row
            ]
        )
    table = Table(formatted, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TABLE_BLUE),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def body_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Italic", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(0.7 * inch, 0.38 * inch, "JanSahay Project Synopsis")
    canvas.drawRightString(7.8 * inch, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    pass


def build():
    logo = make_logo()
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=11,
            leading=15,
            textColor=TEXT,
            alignment=TA_LEFT,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeadingCustom",
            parent=styles["Heading2"],
            fontName="Times-Bold",
            fontSize=14,
            leading=17,
            textColor=BLUE,
            spaceBefore=5,
            spaceAfter=5,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubHeadingCustom",
            parent=styles["Heading3"],
            fontName="Times-Bold",
            fontSize=12,
            leading=15,
            textColor=BLUE,
            spaceBefore=4,
            spaceAfter=4,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableCustom",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=11.5,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TableHeaderCustom",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=9.5,
            leading=11.5,
            textColor=TEXT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverUniversity",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=16,
            leading=19,
            textColor=TEXT,
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverDepartment",
            parent=styles["Normal"],
            fontName="Times-Italic",
            fontSize=13,
            leading=16,
            textColor=TEXT,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=17,
            leading=21,
            textColor=BLUE,
            alignment=TA_CENTER,
            spaceAfter=17,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverProject",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=15,
            leading=18,
            textColor=TEXT,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubtitle",
            parent=styles["Normal"],
            fontName="Times-Italic",
            fontSize=12,
            leading=15,
            textColor=TEXT,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSmall",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=11,
            leading=15,
            textColor=TEXT,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverNames",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=12,
            leading=17,
            textColor=TEXT,
            alignment=TA_CENTER,
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.65 * inch,
        title="JanSahay Project Synopsis",
        author="Dhruv, Dev and Devender",
    )

    story = []
    story.extend(
        [
            paragraph("DEENBANDHU CHHOTU RAM UNIVERSITY OF SCIENCE AND TECHNOLOGY, MURTHAL", styles["CoverUniversity"]),
            Spacer(1, 0.08 * inch),
            paragraph("Department of Computer Science and Engineering", styles["CoverDepartment"]),
            Spacer(1, 0.32 * inch),
        ]
    )
    if logo:
        story.append(RLImage(str(logo), width=2.25 * inch, height=2.30 * inch))
    else:
        story.append(Spacer(1, 2.30 * inch))
    story.extend(
        [
            Spacer(1, 0.42 * inch),
            paragraph("PROJECT SYNOPSIS", styles["CoverTitle"]),
            paragraph("JanSahay", styles["CoverProject"]),
            paragraph("An AI-Based Personalized Government Service Eligibility and Navigation System", styles["CoverSubtitle"]),
            Spacer(1, 0.95 * inch),
            paragraph("Submitted by", styles["CoverSmall"]),
            Spacer(1, 0.05 * inch),
            paragraph("Dev - 23001001022<br/>Devender - 23001001023<br/>Dhruv - 23001001024", styles["CoverNames"]),
            Spacer(1, 0.48 * inch),
            paragraph("Under the Guidance of", styles["CoverSmall"]),
            Spacer(1, 0.05 * inch),
            paragraph("Dr. Dinesh Singh", styles["CoverNames"]),
            PageBreak(),
        ]
    )

    h = styles["HeadingCustom"]
    sh = styles["SubHeadingCustom"]
    b = styles["BodyCustom"]

    story.extend(
        [
            paragraph("1. Introduction", h),
            paragraph(
                "Government welfare schemes and public services can provide significant support for education, agriculture, healthcare, housing, employment, and social security. However, citizens often struggle to identify the schemes relevant to their personal circumstances because information is distributed across multiple portals, departments, documents, and eligibility conditions. The terminology used in official guidelines can also make the discovery process difficult for first-time users.",
                b,
            ),
            paragraph(
                "JanSahay is proposed as a web-based, intelligent platform that converts a citizen's profile and natural-language request into understandable, explainable, and actionable scheme recommendations. The system combines a curated government-scheme knowledge base, a deterministic eligibility engine, NLP-based semantic search, document intelligence, and an application navigator. The first version will focus on Central Government and Haryana schemes and will act as a guidance and discovery platform rather than an official government application portal.",
                b,
            ),
            paragraph("2. Existing System and Motivation", h),
            paragraph(
                "Existing government portals generally provide scheme information through department-wise pages, static search, or long eligibility documents. Citizens may need to visit several portals and interpret rules independently. Manual assistance through offices, help desks, or informal intermediaries remains useful but is time-consuming and difficult to scale. Generic search engines return broad results but do not reliably connect a citizen's age, income, occupation, location, family situation, and documents with scheme-specific conditions.",
                b,
            ),
            paragraph(
                "The motivation for JanSahay is to provide a single, accessible, and explainable interface that reduces information overload while keeping final decisions tied to stored eligibility rules and official sources. The project also creates a practical research and engineering problem involving structured data, rule reasoning, information retrieval, NLP, document processing, and human-centred design.",
                b,
            ),
            paragraph("3. Problem Statement", h),
            paragraph("Citizens face several recurring problems that this project aims to solve:", b),
            *bullets(
                [
                    "No unified view of relevant government schemes across departments and categories.",
                    "Difficulty understanding eligibility requirements written in lengthy or technical language.",
                    "Lack of personalized recommendations based on a citizen's complete profile.",
                    "Unclear reasons for eligibility, ineligibility, or missing information.",
                    "Repeated effort in identifying, preparing, and validating required documents.",
                    "No clear step-by-step guidance from scheme discovery to the official application pathway.",
                    "Limited analytics for understanding common citizen needs and ineligibility reasons.",
                ],
                b,
            ),
            paragraph("4. Objectives", h),
            paragraph("The primary objectives of this project are to:", b),
            *bullets(
                [
                    "Design and develop a secure web application for personalized government-service discovery.",
                    "Create a structured and verifiable knowledge base for 30-50 Central Government and Haryana schemes.",
                    "Implement an eligibility engine that returns Eligible, Potentially Eligible, or Not Eligible results.",
                    "Explain each result by showing satisfied conditions, failed conditions, and missing information.",
                    "Use NLP and semantic retrieval to understand natural-language requests in English and Hinglish-oriented inputs.",
                    "Provide document upload, text extraction, document-type identification, and basic field validation.",
                    "Guide citizens through required documents and the official application process without simulating unauthorized submissions.",
                    "Evaluate recommendation quality, eligibility accuracy, document extraction, and system response time.",
                ],
                b,
            ),
        ]
    )

    story.extend(
        [
            paragraph("5. Scope of the Project", h),
            paragraph(
                "The initial scope covers a curated catalogue of 30-50 schemes and services from the Central Government and Haryana Government across agriculture, education, healthcare, housing, employment, financial assistance, and social security. The platform will support citizen profiles, scheme search, natural-language discovery, rule-based eligibility assessment, explanations, document management, official source links, and an administrator dashboard. Each scheme record will include its department, beneficiary group, conditions, benefits, required documents, application process, official source URL, and last verified date.",
                b,
            ),
            paragraph(
                "The project is intended for local deployment and academic demonstration. It will not claim to cover every Indian scheme, provide automatic government approval, make legal or medical decisions, or submit applications to government departments without an authorized API. These boundaries keep the prototype feasible, safe, and verifiable within the project timeline.",
                b,
            ),
            paragraph("6. Proposed System", h),
            paragraph(
                "The proposed system is a full-stack web application built around a citizen profile, a structured scheme knowledge base, and a hybrid recommendation pipeline. Natural language is used to understand intent and retrieve relevant schemes, while eligibility decisions are generated from explicit rules and recorded profile data.",
                b,
            ),
            paragraph("6.1 Citizen", sh),
            paragraph(
                "Citizens can register, maintain personal and family details, enter information such as age, income, occupation, location, education, land, and existing benefits, and browse or search schemes. They can view eligibility results with explanations, upload documents, track document readiness, and follow the official application steps for a selected scheme.",
                b,
            ),
            paragraph("6.2 Administrator / Scheme Analyst", sh),
            paragraph(
                "The administrator can manage scheme records, eligibility rules, categories, required documents, official links, and verification dates. The dashboard can display user activity, popular categories, eligibility-check counts, and common reasons for ineligibility. Administrative controls will be separated from citizen functions through role-based access control.",
                b,
            ),
            paragraph("6.3 Intelligent Eligibility and Navigation Layer", sh),
            paragraph(
                "The system parses a citizen's request, identifies relevant intent and entities, retrieves semantically similar schemes, applies explicit eligibility rules, and generates an explanation. The application navigator then presents a checklist of documents and ordered actions. The AI layer assists with language understanding and retrieval; it does not replace the rule engine for final eligibility reasoning.",
                b,
            ),
            paragraph("7. Data Model (Key Entities)", h),
            paragraph("The system's data model is organized around the following core entities:", b),
            make_table(
                [
                    ["Entity", "Key Attributes"],
                    ["Citizen Profile", "Citizen ID, Name, Age, State, District, Income, Occupation, Education, Family Details, Land Details"],
                    ["Scheme", "Scheme ID, Name, Department, Category, Scope, Benefits, Rules, Documents, Official URL, Verification Date"],
                    ["Eligibility Check", "Check ID, Citizen ID, Scheme ID, Result, Matched Conditions, Failed Conditions, Missing Information, Timestamp"],
                    ["Document Record", "Document ID, Citizen ID, Type, File Reference, Extracted Fields, Validation Status, Expiry Date"],
                    ["Recommendation", "Recommendation ID, Citizen ID, Query, Intent, Ranked Schemes, Relevance Score, Explanation"],
                ],
                [1.5 * inch, 5.35 * inch],
                {"table": styles["TableCustom"], "table_header": styles["TableHeaderCustom"]},
            ),
            Spacer(1, 8),
            paragraph("8. Technology Stack", h),
            make_table(
                [
                    ["Layer", "Technology"],
                    ["Frontend / UI", "React with JavaScript or TypeScript, HTML, CSS, and a responsive component library"],
                    ["Backend / API", "Python, FastAPI, Uvicorn, and REST APIs"],
                    ["Database", "PostgreSQL for citizen profiles, schemes, rules, documents, and audit records"],
                    ["ORM / Migrations", "SQLAlchemy for database access and Alembic for versioned schema migrations"],
                    ["Authentication / Security", "JWT, password hashing with bcrypt or Argon2, RBAC, CORS, and environment-based secrets"],
                    ["Validation / API Schemas", "Pydantic models for request validation, response schemas, and configuration"],
                    ["Eligibility Engine", "Custom Python rule engine with versioned JSON-based scheme conditions and explanation output"],
                    ["NLP / Retrieval", "Sentence Transformers with FAISS or pgvector for semantic search and recommendation ranking"],
                    ["Document Intelligence", "Tesseract OCR, PyMuPDF or pdfplumber, python-multipart, and basic field/date validation"],
                    ["Caching / Background Jobs", "Redis for caching; Celery with Redis as broker for OCR, notifications, and report jobs (optional)"],
                    ["Testing", "Pytest, FastAPI TestClient, HTTPX, and frontend component tests"],
                    ["Deployment / Version Control", "Docker, Docker Compose, environment-based configuration, and Git"],
                ],
                [1.9 * inch, 4.95 * inch],
                {"table": styles["TableCustom"], "table_header": styles["TableHeaderCustom"]},
            ),
        ]
    )

    story.extend(
        [
            paragraph("9. Core System Features", h),
            *bullets(
                [
                    "Role-based authentication for Citizens and Administrators.",
                    "Citizen profile creation with personal, family, economic, educational, and location information.",
                    "Curated scheme catalogue with category filters, official source links, and verification metadata.",
                    "Rule-based eligibility validation with three-level result status and condition-wise explanation.",
                    "Natural-language scheme discovery using intent recognition and semantic retrieval.",
                    "Document upload, OCR-based text extraction, type detection, and basic name, date, and field checks.",
                    "Personalized dashboard showing identified schemes, missing information, document readiness, and next actions.",
                    "Step-by-step application navigator that directs users to the official application channel.",
                    "Administrator analytics for scheme usage, request categories, and frequent ineligibility reasons.",
                    "Audit-friendly storage of rule versions, source URLs, and last verified dates.",
                    "Validated REST APIs, secure file handling, automated tests, and Docker-based local deployment.",
                    "Optional Redis caching and Celery background jobs for document processing, notifications, and report generation.",
                ],
                b,
            ),
            paragraph("10. Proposed Methodology and Work Plan", h),
            paragraph("The project will be developed iteratively across the following phases:", b),
            make_table(
                [
                    ["Phase", "Activities", "Approx. Duration"],
                    ["1", "Requirement analysis, scheme-domain selection, user journeys, and ethical boundaries", "1-2 weeks"],
                    ["2", "Scheme research, rule formalization, database schema, and seed-data preparation", "2 weeks"],
                    ["3", "Development of authentication, citizen profiles, ORM models, migrations, scheme APIs, and administrator APIs", "3 weeks"],
                    ["4", "Implementation and testing of the eligibility engine and explanation generator", "3 weeks"],
                    ["5", "Integration of NLP intent understanding, semantic retrieval, and recommendation ranking", "3 weeks"],
                    ["6", "Document OCR, validation workflow, optional background jobs/caching, dashboard integration, and usability refinement", "3 weeks"],
                    ["7", "Evaluation, deployment, documentation, presentation, and final demonstration", "2 weeks"],
                ],
                [0.55 * inch, 5.25 * inch, 1.05 * inch],
                {"table": styles["TableCustom"], "table_header": styles["TableHeaderCustom"]},
            ),
            Spacer(1, 8),
            paragraph("11. Expected Outcome", h),
            paragraph(
                "On completion, the project will deliver a working prototype that helps a citizen discover relevant government schemes through a guided profile and natural-language interface. The system will provide transparent eligibility results, show why a scheme was recommended or rejected, identify missing documents, and direct the citizen to the official application process. The project will also provide an administrator view of scheme data and anonymized usage trends. The prototype will be evaluated using manually prepared test profiles, labeled recommendation queries, document samples, and basic performance measurements.",
                b,
            ),
            paragraph("12. Future Scope", h),
            *bullets(
                [
                    "Expansion from Haryana and Central Government schemes to additional states and departments.",
                    "Voice-based interaction with Hindi and multilingual speech-to-text and text-to-speech support.",
                    "Integration with authorized government APIs for application submission and status tracking.",
                    "Continuous scheme-update pipelines with source-change detection and administrator review.",
                    "Improved document validation using more advanced vision-language models and fraud checks.",
                    "Mobile application and assisted-access modes for low-connectivity or low-literacy users.",
                    "Advanced analytics for estimating unmet needs and improving public-service discoverability.",
                ],
                b,
            ),
            paragraph("13. References", h),
            paragraph("MyScheme Portal - https://www.myscheme.gov.in/", b),
            paragraph("National Portal of India - https://www.india.gov.in/", b),
            paragraph("Government of Haryana - https://haryana.gov.in/", b),
            paragraph("FastAPI Documentation - https://fastapi.tiangolo.com/", b),
            paragraph("React Documentation - https://react.dev/", b),
            paragraph("SQLAlchemy Documentation - https://www.sqlalchemy.org/", b),
            paragraph("Alembic Documentation - https://alembic.sqlalchemy.org/", b),
            paragraph("Pydantic Documentation - https://docs.pydantic.dev/", b),
            paragraph("Sentence Transformers Documentation - https://www.sbert.net/", b),
            paragraph("Tesseract OCR Documentation - https://tesseract-ocr.github.io/", b),
            paragraph("Redis Documentation - https://redis.io/docs/", b),
            paragraph("Celery Documentation - https://docs.celeryq.dev/", b),
            paragraph("Pytest Documentation - https://docs.pytest.org/", b),
        ]
    )

    doc.build(story, onFirstPage=cover_page, onLaterPages=body_page)
    print(OUTPUT)


if __name__ == "__main__":
    build()
