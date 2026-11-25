from sqlalchemy import inspect, select, text
from sqlalchemy.orm import Session

from .database import Base, engine
from .models import CitizenProfile, Scheme, User
from .scheme_data import SCHEMES
from .security import hash_password


ADMIN_EMAIL = "admin@jansahay.in"
LEGACY_ADMIN_EMAIL = "admin@jansahay.local"


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_schema()
    with Session(engine) as db:
        _rename_legacy_schemes(db)
        _seed_users(db)
        _seed_schemes(db)
        _sync_scheme_metadata(db)
        db.commit()


def _ensure_schema() -> None:
    additions = {
        "citizen_profiles": {
            "social_category": "VARCHAR(30)",
            "residence_type": "VARCHAR(20)",
            "housing_status": "VARCHAR(80)",
            "marital_status": "VARCHAR(30)",
            "disability_percent": "FLOAT",
            "pregnant": "BOOLEAN",
            "girl_children": "INTEGER",
            "only_girl_children": "BOOLEAN",
            "marks_percentage": "FLOAT",
            "has_family_id": "BOOLEAN",
            "breadwinner_deceased": "BOOLEAN",
            "existing_benefits": "JSON",
        },
        "schemes": {"conflicts": "JSON", "application_portal_url": "VARCHAR(500)"},
        "documents": {"extracted_fields": "JSON"},
    }
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in additions.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, sql_type in columns.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}"))


def _rename_legacy_schemes(db: Session) -> None:
    legacy_names = {
        "NSP-SCHOLARSHIP": "PM-USP",
        "NSAP-PENSION": "IGNOAPS",
    }
    for old_code, new_code in legacy_names.items():
        legacy = db.scalar(select(Scheme).where(Scheme.code == old_code))
        if legacy:
            legacy.code = new_code


def _seed_users(db: Session) -> None:
    admin = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
    legacy_admin = db.scalar(select(User).where(User.email == LEGACY_ADMIN_EMAIL))
    if admin is None and legacy_admin is not None:
        legacy_admin.email = ADMIN_EMAIL
        admin = legacy_admin
    if admin is None:
        db.add(User(full_name="JanSahay Administrator", email=ADMIN_EMAIL, password_hash=hash_password("admin123"), role="admin"))
    if db.scalar(select(User).where(User.email == "citizen@example.com")) is None:
        citizen = User(full_name="Ramesh Kumar", email="citizen@example.com", password_hash=hash_password("demo123"), role="citizen")
        db.add(citizen)
        db.flush()
        db.add(CitizenProfile(
            user_id=citizen.id,
            age=45,
            state="Haryana",
            district="Sonipat",
            annual_income=240000,
            occupation="farmer",
            education_level="Graduate",
            gender="Male",
            family_size=4,
            land_acres=3,
            disability=False,
            student=False,
            has_bank_account=True,
        ))


def _seed_schemes(db: Session) -> None:
    existing = {code for (code,) in db.execute(select(Scheme.code)).all()}
    for data in SCHEMES:
        if data["code"] not in existing:
            db.add(Scheme(**data))


def _sync_scheme_metadata(db: Session) -> None:
    for data in SCHEMES:
        scheme = db.scalar(select(Scheme).where(Scheme.code == data["code"]))
        if scheme:
            for key, value in data.items():
                setattr(scheme, key, value)
            # Rows created before conflict-aware rules had this JSON column as NULL.
            scheme.conflicts = data.get("conflicts") or []
            scheme.application_steps = data.get("application_steps") or []
            scheme.required_documents = data.get("required_documents") or []
            scheme.rules = data.get("rules") or []
            scheme.application_portal_url = data.get("application_portal_url")

