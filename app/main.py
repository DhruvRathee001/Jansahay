from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import re
import shutil
import asyncio
import sys
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import CitizenProfile, Document, EligibilityCheck, Scheme, User
from .recommendation import recommend
from .rules import evaluate_scheme
from .schemas import (
    DocumentOut,
    AdminSchemeCreate,
    AdminSchemeUpdate,
    LoginRequest,
    ProfileOut,
    ProfileUpdate,
    RecommendationRequest,
    SchemeOut,
    TokenResponse,
    UserCreate,
    UserOut,
)
from .security import create_access_token, get_current_user, get_optional_user, hash_password, require_admin, verify_password
from .seed import init_db


if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
    # Selector avoids a Proactor socketpair stall in local Windows test/server runs.
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="JanSahay API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name, "time": datetime.now(timezone.utc).isoformat()}


@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password), role="citizen")
    db.add(user)
    db.flush()
    db.add(CitizenProfile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return {"access_token": create_access_token(user), "user": user}


@app.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token(user), "user": user}


@app.get("/api/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@app.get("/api/profile", response_model=ProfileOut)
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _get_or_create_profile(db, user)


@app.put("/api/profile", response_model=ProfileOut)
def update_profile(payload: ProfileUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, user)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


@app.get("/api/schemes", response_model=list[SchemeOut])
def list_schemes(
    q: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=80),
    eligibility: str | None = Query(default=None, pattern="^(ELIGIBLE|POTENTIALLY_ELIGIBLE|NOT_ELIGIBLE)$"),
    scope: str | None = Query(default=None, pattern="^(Central Government|Haryana Government)$"),
    sort: str = Query(default="eligibility", pattern="^(eligibility|name|category)$"),
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    stmt = select(Scheme).where(Scheme.is_active.is_(True)).order_by(Scheme.category, Scheme.name)
    if category:
        stmt = stmt.where(Scheme.category == category)
    if scope:
        stmt = stmt.where(Scheme.scope == scope)
    if q:
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(Scheme.name.ilike(term), Scheme.summary.ilike(term), Scheme.category.ilike(term), Scheme.benefits.ilike(term)))
    schemes = list(db.scalars(stmt).all())
    enriched = []
    for scheme in schemes:
        payload = _scheme_payload(scheme)
        if user:
            result = evaluate_scheme(scheme, _get_or_create_profile(db, user))
            payload["eligibility_status"] = result.status
            payload["eligibility_score"] = result.score
        if eligibility and payload.get("eligibility_status") != eligibility:
            continue
        enriched.append(payload)
    if sort == "name":
        enriched.sort(key=lambda item: item["name"].lower())
    elif sort == "category":
        enriched.sort(key=lambda item: (item["category"].lower(), item["name"].lower()))
    else:
        rank = {"ELIGIBLE": 0, "POTENTIALLY_ELIGIBLE": 1, "NOT_ELIGIBLE": 2}
        enriched.sort(key=lambda item: (rank.get(item.get("eligibility_status"), 3), -(item.get("eligibility_score") or 0), item["name"].lower()))
    return enriched


@app.get("/api/schemes/{scheme_id}", response_model=SchemeOut)
def get_scheme(scheme_id: int, db: Session = Depends(get_db)):
    scheme = db.get(Scheme, scheme_id)
    if not scheme or not scheme.is_active:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


@app.post("/api/eligibility/check/{scheme_id}")
def check_eligibility(scheme_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scheme = db.get(Scheme, scheme_id)
    if not scheme or not scheme.is_active:
        raise HTTPException(status_code=404, detail="Scheme not found")
    profile = _get_or_create_profile(db, user)
    result = evaluate_scheme(scheme, profile)
    record = EligibilityCheck(
        user_id=user.id,
        scheme_id=scheme.id,
        status=result.status,
        score=result.score,
        matched_conditions=result.matched,
        failed_conditions=result.failed,
        missing_information=result.missing,
    )
    db.add(record)
    db.commit()
    return {
        "scheme": _scheme_payload(scheme),
        "status": result.status,
        "score": result.score,
        "matched_conditions": result.matched,
        "failed_conditions": result.failed,
        "missing_information": result.missing,
        "next_action": _next_action(result.status, scheme),
    }


@app.post("/api/recommendations")
def recommendations(payload: RecommendationRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, user)
    schemes = list(db.scalars(select(Scheme).where(Scheme.is_active.is_(True))).all())
    results = recommend(payload.query, schemes, profile)
    formatted = [
        {
            "scheme": _scheme_payload(item["scheme"]),
            "relevance_score": item["relevance_score"],
            "eligibility": item["eligibility"],
            "eligibility_score": item["eligibility_score"],
            "why": item["why"],
        }
        for item in results
    ]
    return {
        "query": payload.query,
        "count": len(results),
        "results": formatted,
        "results_by_scope": {
            "Central Government": [item for item in formatted if item["scheme"]["scope"] == "Central Government"],
            "Haryana Government": [item for item in formatted if item["scheme"]["scope"] == "Haryana Government"],
        },
    }


@app.get("/api/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(db, user)
    schemes = list(db.scalars(select(Scheme).where(Scheme.is_active.is_(True))).all())
    counts = {"ELIGIBLE": 0, "POTENTIALLY_ELIGIBLE": 0, "NOT_ELIGIBLE": 0}
    quick_matches = []
    matches_by_scope = {"Central Government": [], "Haryana Government": []}
    for scheme in schemes:
        result = evaluate_scheme(scheme, profile)
        counts[result.status] += 1
        if result.status in {"ELIGIBLE", "POTENTIALLY_ELIGIBLE"}:
            match = {"scheme": _scheme_payload(scheme), "status": result.status, "score": result.score}
            quick_matches.append(match)
            matches_by_scope[scheme.scope].append(match)
    for scope_matches in matches_by_scope.values():
        scope_matches.sort(key=lambda item: (item["status"] != "ELIGIBLE", -item["score"], item["scheme"]["name"]))
    return {
        "profile": profile,
        "scheme_count": len(schemes),
        "counts": counts,
        "matches": quick_matches[:6],
        "matches_by_scope": {key: value[:6] for key, value in matches_by_scope.items()},
    }


@app.get("/api/documents", response_model=list[DocumentOut])
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.uploaded_at.desc())).all()


@app.post("/api/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {"pdf", "png", "jpg", "jpeg", "txt"}
    original_name = Path(file.filename or "document").name
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if extension not in allowed:
        raise HTTPException(status_code=400, detail="Upload a PDF, image, or text document")
    stored_name = f"{uuid4().hex}_{re.sub(r'[^a-zA-Z0-9._-]', '_', original_name)}"
    destination = settings.upload_dir / stored_name
    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    extracted_text, validation, extracted_fields = _extract_document_text(destination, extension, document_type)
    record = Document(
        user_id=user.id,
        document_type=document_type.strip()[:80],
        file_name=original_name[:255],
        stored_path=str(destination),
        extracted_text=extracted_text,
        extracted_fields=extracted_fields,
        validation_status=validation,
    )
    db.add(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=409, detail="This document has already been uploaded")
    db.refresh(record)
    return record


@app.post("/api/documents/{document_id}/apply-to-profile", response_model=ProfileOut)
def apply_document_fields(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    profile = _get_or_create_profile(db, user)
    allowed_fields = {
        "age", "state", "annual_income", "land_acres", "disability_percent", "marks_percentage", "education_level", "has_bank_account"
    }
    applied = {key: value for key, value in (document.extracted_fields or {}).items() if key in allowed_fields}
    for key, value in applied.items():
        setattr(profile, key, value)
    if "disability_percent" in applied:
        profile.disability = applied["disability_percent"] >= 40
    db.commit()
    db.refresh(profile)
    return profile


@app.post("/api/documents/{document_id}/process-ocr", response_model=DocumentOut)
def process_document_ocr(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(document.stored_path)
    extension = path.suffix.lower().lstrip(".")
    extracted_text, validation, extracted_fields = _extract_document_text(path, extension, document.document_type)
    document.extracted_text = extracted_text
    document.extracted_fields = extracted_fields
    document.validation_status = validation
    db.commit()
    db.refresh(document)
    return document


@app.get("/api/admin/metrics")
def admin_metrics(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    categories = db.execute(select(Scheme.category, func.count(Scheme.id)).group_by(Scheme.category)).all()
    statuses = db.execute(select(EligibilityCheck.status, func.count(EligibilityCheck.id)).group_by(EligibilityCheck.status)).all()
    return {
        "users": db.scalar(select(func.count(User.id))) or 0,
        "active_users": db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0,
        "admin_users": db.scalar(select(func.count(User.id)).where(User.role == "admin")) or 0,
        "schemes": db.scalar(select(func.count(Scheme.id)).where(Scheme.is_active.is_(True))) or 0,
        "active_schemes": db.scalar(select(func.count(Scheme.id)).where(Scheme.is_active.is_(True))) or 0,
        "inactive_schemes": db.scalar(select(func.count(Scheme.id)).where(Scheme.is_active.is_(False))) or 0,
        "eligibility_checks": db.scalar(select(func.count(EligibilityCheck.id))) or 0,
        "categories": {key: value for key, value in categories},
        "eligibility_statuses": {key: value for key, value in statuses},
    }


@app.get("/api/admin/users")
def admin_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    result = []
    for account in users:
        result.append({
            "id": account.id,
            "full_name": account.full_name,
            "email": account.email,
            "role": account.role,
            "is_active": account.is_active,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "documents": db.scalar(select(func.count(Document.id)).where(Document.user_id == account.id)) or 0,
            "eligibility_checks": db.scalar(select(func.count(EligibilityCheck.id)).where(EligibilityCheck.user_id == account.id)) or 0,
        })
    return result


@app.get("/api/admin/checks")
def admin_checks(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = db.execute(
        select(EligibilityCheck, User.full_name, User.email, Scheme.name)
        .join(User, User.id == EligibilityCheck.user_id)
        .join(Scheme, Scheme.id == EligibilityCheck.scheme_id)
        .order_by(EligibilityCheck.created_at.desc())
        .limit(200)
    ).all()
    return [
        {
            "id": check.id,
            "user_name": full_name,
            "user_email": email,
            "scheme_name": scheme_name,
            "status": check.status,
            "score": check.score,
            "created_at": check.created_at.isoformat() if check.created_at else None,
        }
        for check, full_name, email, scheme_name in rows
    ]


@app.get("/api/admin/schemes")
def admin_list_schemes(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    schemes = db.scalars(select(Scheme).order_by(Scheme.is_active.desc(), Scheme.category, Scheme.name)).all()
    return [_admin_scheme_payload(scheme) for scheme in schemes]


@app.post("/api/admin/schemes", status_code=status.HTTP_201_CREATED)
def admin_create_scheme(payload: AdminSchemeCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    scheme = Scheme(**payload.model_dump())
    db.add(scheme)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A scheme with this code already exists")
    db.refresh(scheme)
    return _admin_scheme_payload(scheme)


@app.put("/api/admin/schemes/{scheme_id}")
def admin_update_scheme(scheme_id: int, payload: AdminSchemeUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    scheme = db.get(Scheme, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(scheme, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A scheme with this code already exists")
    db.refresh(scheme)
    return _admin_scheme_payload(scheme)


@app.delete("/api/admin/schemes/{scheme_id}")
def admin_delete_scheme(scheme_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    scheme = db.get(Scheme, scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    # Soft-delete preserves historical eligibility checks for auditability.
    scheme.is_active = False
    db.commit()
    db.refresh(scheme)
    return _admin_scheme_payload(scheme)


def _get_or_create_profile(db: Session, user: User) -> CitizenProfile:
    profile = db.scalar(select(CitizenProfile).where(CitizenProfile.user_id == user.id))
    if not profile:
        profile = CitizenProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _scheme_payload(scheme: Scheme) -> dict:
    return {
        "id": scheme.id,
        "code": scheme.code,
        "name": scheme.name,
        "department": scheme.department,
        "category": scheme.category,
        "scope": scheme.scope,
        "summary": scheme.summary,
        "benefits": scheme.benefits,
        "application_steps": scheme.application_steps,
        "required_documents": scheme.required_documents,
        "rules": scheme.rules,
        "conflicts": scheme.conflicts,
        "official_url": scheme.official_url,
        "application_portal_url": scheme.application_portal_url,
        "source_verified_on": scheme.source_verified_on,
    }


def _admin_scheme_payload(scheme: Scheme) -> dict:
    payload = _scheme_payload(scheme)
    payload["is_active"] = scheme.is_active
    return payload


def _next_action(result: str, scheme: Scheme) -> str:
    if result == "ELIGIBLE":
        return f"Prepare the required documents and continue through the official {scheme.name} application channel."
    if result == "POTENTIALLY_ELIGIBLE":
        return "Complete the missing profile information or documents, then run the eligibility check again."
    return "Review the failed conditions and explore other schemes that may better match your profile."


def _extract_document_text(path: Path, extension: str, document_type: str) -> tuple[str | None, str, dict]:
    text = None
    if extension == "txt":
        text = path.read_text(encoding="utf-8", errors="ignore")[:20_000]
    try:
        from pypdf import PdfReader

        if extension == "pdf":
            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)[:20_000]
    except Exception:
        pass
    if extension in {"png", "jpg", "jpeg"}:
        try:
            from PIL import Image
            import pytesseract

            if settings.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
            text = pytesseract.image_to_string(Image.open(path))[:20_000]
        except ImportError:
            return None, "OCR_UNAVAILABLE", {"document_type": document_type, "ocr_error": "Install Pillow and Tesseract OCR to process image documents."}
        except Exception:
            return None, "OCR_UNAVAILABLE", {"document_type": document_type, "ocr_error": "Tesseract OCR is not installed or could not read this image."}
    if not text:
        return None, "UPLOADED_OCR_PENDING", {"document_type": document_type}
    return text, "TEXT_EXTRACTED", _extract_fields(text, document_type)


def _extract_fields(text: str, document_type: str) -> dict:
    fields = {"document_type": document_type}
    income = re.search(r"(?:annual\s+income|income|aay|bpl)[^\d₹]{0,20}[₹Rs\.\s]*([\d,]+)", text, re.I)
    land = re.search(r"(?:land|area|acre|hectare)[^\d]{0,20}(\d+(?:\.\d+)?)\s*(?:acre|acres|hectare|hectares)?", text, re.I)
    dob = re.search(r"(?:dob|date\s+of\s+birth)[^\d]{0,20}(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text, re.I)
    age = re.search(r"(?:age)[^\d]{0,20}(\d{1,3})", text, re.I)
    disability = re.search(r"(?:disability|benchmark)[^\d]{0,20}(\d{1,3})\s*%", text, re.I)
    marks = re.search(r"(?:marks|percentage|score|aggregate)[^\d]{0,20}(\d{1,3}(?:\.\d+)?)\s*%", text, re.I)
    if income:
        fields["annual_income"] = float(income.group(1).replace(",", ""))
    if land:
        fields["land_acres"] = float(land.group(1))
    if dob:
        try:
            birth_date = datetime(int(dob.group(3)), int(dob.group(2)), int(dob.group(1)), tzinfo=timezone.utc)
            today = datetime.now(timezone.utc)
            fields["age"] = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        except ValueError:
            pass
    elif age and int(age.group(1)) <= 120:
        fields["age"] = int(age.group(1))
    if disability:
        fields["disability_percent"] = float(disability.group(1))
    if marks and float(marks.group(1)) <= 100:
        fields["marks_percentage"] = float(marks.group(1))
    education_levels = {"10th marksheet": "10th", "12th marksheet": "12th", "graduation marksheet/degree": "Graduate"}
    if document_type.lower() in education_levels:
        fields["education_level"] = education_levels[document_type.lower()]
    if document_type.lower() == "bank account proof":
        fields["has_bank_account"] = True
    for state in ("Haryana", "Punjab", "Delhi", "Uttar Pradesh", "Rajasthan"):
        if state.lower() in text.lower():
            fields["state"] = state
            break
    return fields

