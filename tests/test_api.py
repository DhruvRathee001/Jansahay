from app.database import SessionLocal
from app.main import (
    _extract_fields,
    admin_create_scheme,
    admin_delete_scheme,
    admin_list_schemes,
    admin_metrics,
    admin_update_scheme,
    admin_users,
    dashboard,
    health,
    list_schemes,
    recommendations,
)
from app.models import CitizenProfile, Scheme, User
from app.schemas import AdminSchemeCreate, AdminSchemeUpdate, RecommendationRequest
from app.seed import init_db
from app.rules import evaluate_scheme
from sqlalchemy import select


init_db()


def demo_context():
    db = SessionLocal()
    user = db.scalar(select(User).where(User.email == "citizen@example.com"))
    return db, user


def test_health():
    assert health()["status"] == "ok"


def test_demo_login_and_profile():
    db, user = demo_context()
    assert user.full_name == "Ramesh Kumar"
    assert user.profile.state == "Haryana"
    db.close()


def test_scheme_catalogue_and_eligibility():
    db, user = demo_context()
    schemes = list_schemes(q=None, category=None, scope=None, eligibility=None, sort="eligibility", user=user, db=db)
    assert len(schemes) == 45
    assert schemes[0]["eligibility_status"] == "ELIGIBLE"
    eligible = list_schemes(q=None, category=None, scope=None, eligibility="ELIGIBLE", sort="eligibility", user=user, db=db)
    assert eligible
    assert all(item["eligibility_status"] == "ELIGIBLE" for item in eligible)
    pm_kisan = db.scalar(select(Scheme).where(Scheme.code == "PM-KISAN"))
    result = evaluate_scheme(pm_kisan, user.profile)
    assert result.status == "ELIGIBLE"
    assert result.score == 100
    db.close()


def test_scope_filters_and_grouped_results():
    db, user = demo_context()
    central = list_schemes(q=None, category=None, scope="Central Government", eligibility=None, sort="name", user=user, db=db)
    haryana = list_schemes(q=None, category=None, scope="Haryana Government", eligibility=None, sort="name", user=user, db=db)
    assert central and haryana
    assert all(item["scope"] == "Central Government" for item in central)
    assert all(item["scope"] == "Haryana Government" for item in haryana)
    dash = dashboard(user, db)
    assert set(dash["matches_by_scope"]) == {"Central Government", "Haryana Government"}
    vivah = db.scalar(select(Scheme).where(Scheme.code == "VIVAH-SHAGUN"))
    assert vivah.official_url == "https://schemes.haryanascbc.gov.in/Citizen/aboutVivahshagun"
    assert vivah.application_portal_url == "https://sewa.haryana.gov.in/state-schemes/mukhya-mantri-vivah-shagun-yojna/"
    db.close()


def test_haryana_conflict_and_ocr_fields():
    db, _ = demo_context()
    old_age = db.scalar(select(Scheme).where(Scheme.code == "HARYANA-OLD-AGE"))
    profile = CitizenProfile(state="Haryana", age=65, annual_income=100000, existing_benefits=["HARYANA-WIDOW"])
    result = evaluate_scheme(old_age, profile)
    assert result.status == "NOT_ELIGIBLE"
    fields = _extract_fields("Annual income: Rs. 180000\nLand area: 3 acres\nDisability: 60%\nDOB: 01/01/1960\nState: Haryana", "Income certificate")
    assert fields["annual_income"] == 180000
    assert fields["land_acres"] == 3
    assert fields["disability_percent"] == 60
    assert fields["age"] >= 65
    assert fields["state"] == "Haryana"
    education_fields = _extract_fields("Aggregate percentage: 82%", "12th marksheet")
    assert education_fields["education_level"] == "12th"
    assert education_fields["marks_percentage"] == 82
    assert _extract_fields("Account holder", "Bank account proof")["has_bank_account"] is True
    db.close()


def test_recommendations():
    db, user = demo_context()
    response = recommendations(RecommendationRequest(query="I am a farmer and need financial support"), user, db)
    assert response["count"] >= 1
    assert response["results"][0]["scheme"]["code"] == "PM-KISAN"
    assert set(response["results_by_scope"]) == {"Central Government", "Haryana Government"}
    db.close()


def test_admin_metrics_users_and_scheme_crud():
    db = SessionLocal()
    admin = db.scalar(select(User).where(User.email == "admin@jansahay.in"))
    metrics = admin_metrics(admin, db)
    assert metrics["admin_users"] >= 1
    assert metrics["active_schemes"] >= 45
    assert len(admin_users(admin, db)) >= 2
    assert len(admin_list_schemes(admin, db)) >= 45

    created = admin_create_scheme(
        AdminSchemeCreate(
            code="TEST-ADMIN-CRUD",
            name="Admin CRUD Test Scheme",
            department="JanSahay Test Department",
            category="Education",
            scope="Central Government",
            summary="Temporary scheme used to verify administrator CRUD.",
            benefits="Testing only",
            official_url="https://example.com/admin-crud-test",
            source_verified_on="2026-11-20",
        ),
        admin,
        db,
    )
    updated = admin_update_scheme(created["id"], AdminSchemeUpdate(name="Updated Admin CRUD Test Scheme"), admin, db)
    assert updated["name"] == "Updated Admin CRUD Test Scheme"
    deleted = admin_delete_scheme(created["id"], admin, db)
    assert deleted["is_active"] is False
    db.delete(db.get(Scheme, created["id"]))
    db.commit()
    db.close()

