# JanSahay

JanSahay is an explainable citizen-support prototype for discovering government schemes and understanding the next application step. It combines a citizen profile, curated scheme catalogue, deterministic eligibility rules, natural-language recommendation, document records, and an official-source navigator.

## What is included

- Citizen registration and JWT login.
- Demo citizen and administrator accounts.
- Profile-based eligibility checks with `ELIGIBLE`, `POTENTIALLY_ELIGIBLE`, and `NOT_ELIGIBLE` results.
- Condition-by-condition explanations showing matched, failed, and missing information.
- 45 seeded Central Government and Haryana schemes across agriculture, education, healthcare, housing, employment, financial assistance, and social security.
- Extended profile attributes for caste/category, rural/urban residence, housing status, PPP/Family ID, pregnancy, widow status, girl children, marks, disability percentage, and existing benefits.
- Haryana threshold and pension-conflict examples, including mutually exclusive Old Age, Widow, and Divyang benefit checks.
- Natural-language recommendation using a transparent lexical/synonym retrieval fallback.
- Document upload for PDF, image, and text files, with PDF text extraction when available.
- Image OCR through Tesseract, with a retry action for documents that were uploaded before OCR was available.
- Role-protected administrator workspace for user counts, eligibility audit status, and scheme management.
- Administrator scheme CRUD with soft-delete and restore, preserving historical eligibility checks.
- Responsive browser interface served by FastAPI.
- SQLite by default, with a `DATABASE_URL` switch for PostgreSQL later.
- Pytest API smoke tests and Docker files for a containerized run.

## Run locally on Windows

Open PowerShell in this folder and run:

```powershell
.\run.ps1
```

Or run the commands manually:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>.

Image OCR also needs the Tesseract OCR Windows package. If Tesseract is not on `PATH`, set its executable path before starting the app, for example:

```powershell
$env:TESSERACT_CMD = "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

After installing the Python requirements and Tesseract, open My documents and click `Process OCR` on an existing image upload. The extracted profile fields can then be applied with `Apply fields`.

The database is created automatically as `jansahay.db`, and the scheme/user seed data is inserted on the first startup.

## Demo accounts

| Role | Email | Password |
| --- | --- | --- |
| Citizen | `citizen@example.com` | `demo123` |
| Administrator | `admin@jansahay.in` | `admin123` |

Use the demo button on the sign-in screen for the pre-filled citizen profile.

## Useful API routes

- `GET /api/health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/profile`
- `PUT /api/profile`
- `GET /api/schemes?eligibility=ELIGIBLE&sort=eligibility` (logged-in users receive eligibility status and score for every scheme)
- `POST /api/recommendations`
- `POST /api/eligibility/check/{scheme_id}`
- `GET /api/dashboard`
- `GET /api/documents`
- `POST /api/documents`
- `POST /api/documents/{document_id}/process-ocr`
- `POST /api/documents/{document_id}/apply-to-profile`
- `GET /api/admin/metrics`
- `GET /api/admin/users`
- `GET /api/admin/checks`
- `GET /api/admin/schemes`
- `POST /api/admin/schemes`
- `PUT /api/admin/schemes/{scheme_id}`
- `DELETE /api/admin/schemes/{scheme_id}` (soft-deactivates a scheme)
- `GET /docs` for the OpenAPI explorer.

## Project structure

```text
app/
  config.py          environment settings
  database.py        SQLAlchemy engine and sessions
  models.py          database entities
  schemas.py         Pydantic request/response models
  security.py        password hashing and JWT authentication
  scheme_data.py     curated seed catalogue
  rules.py           explainable eligibility engine
  recommendation.py  natural-language retrieval/ranking
  seed.py            database bootstrap and demo data
  main.py            FastAPI routes and document workflow
frontend/
  index.html         application shell
  styles.css         responsive visual system
  app.js             browser application logic
tests/
  test_api.py        API smoke tests
```

## Scheme catalogue note

The detailed 45-name list supplied for this implementation contains 28 Central Government and 17 Haryana Government entries, even though its introductory sentence says 25 + 20. The application keeps all 45 named schemes. The thresholds in the prototype are rule-engine demonstration values and must be reviewed against the current official notification before public use.

## Important project boundary

The prototype is a discovery and navigation tool. It does not approve benefits, make legal/medical decisions, or submit applications to government departments without an authorized integration. Scheme rules and thresholds are demo knowledge-base entries and must be reviewed against current official guidance before public use.

## Next production upgrades

1. Replace demo scheme thresholds with reviewed rule records and source-change workflow.
2. Add Alembic migrations, PostgreSQL, Redis/Celery, object storage, and a real OCR worker.
3. Add sentence-transformer embeddings and a labeled evaluation set for precision@K and recall@K.
4. Add immutable admin audit logs, rate limiting, privacy consent, and deployment secrets.

