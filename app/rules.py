from dataclasses import dataclass
from typing import Any

from .models import CitizenProfile, Scheme


@dataclass
class EligibilityResult:
    status: str
    score: float
    matched: list[dict[str, Any]]
    failed: list[dict[str, Any]]
    missing: list[dict[str, Any]]


def profile_values(profile: CitizenProfile | None) -> dict[str, Any]:
    if not profile:
        return {}
    return {
        "age": profile.age,
        "state": profile.state,
        "district": profile.district,
        "annual_income": profile.annual_income,
        "occupation": (profile.occupation or "").strip().lower() or None,
        "education_level": profile.education_level,
        "social_category": profile.social_category,
        "residence_type": profile.residence_type,
        "housing_status": profile.housing_status,
        "gender": profile.gender,
        "marital_status": profile.marital_status,
        "family_size": profile.family_size,
        "land_acres": profile.land_acres,
        "disability": profile.disability,
        "disability_percent": profile.disability_percent,
        "pregnant": profile.pregnant,
        "girl_children": profile.girl_children,
        "only_girl_children": profile.only_girl_children,
        "marks_percentage": profile.marks_percentage,
        "has_family_id": profile.has_family_id,
        "breadwinner_deceased": profile.breadwinner_deceased,
        "student": profile.student,
        "has_bank_account": profile.has_bank_account,
        "existing_benefits": profile.existing_benefits or [],
        "gender_or_disability": (str(profile.gender or "").lower() == "female") or bool(profile.disability),
        "gender_or_reserved": (str(profile.gender or "").lower() == "female") or str(profile.social_category or "").upper() in {"SC", "ST"},
    }


def evaluate_scheme(scheme: Scheme, profile: CitizenProfile | None) -> EligibilityResult:
    values = profile_values(profile)
    matched: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    for rule in scheme.rules or []:
        field = rule["field"]
        operator = rule["operator"]
        expected = rule.get("value")
        label = rule.get("label", field)
        actual = values.get(field)
        result = _evaluate(actual, operator, expected)
        item = {"field": field, "label": label, "operator": operator, "expected": expected, "actual": actual}
        if result is None:
            missing.append(item)
        elif result:
            matched.append(item)
        else:
            failed.append(item)

    existing_benefits = {str(item).strip().lower() for item in values.get("existing_benefits", [])}
    for conflict in scheme.conflicts or []:
        conflict_text = str(conflict).strip().lower()
        if conflict_text and any(conflict_text in benefit or benefit in conflict_text for benefit in existing_benefits):
            failed.append({
                "field": "existing_benefits",
                "label": f"No conflicting benefit already active: {conflict}",
                "operator": "conflict",
                "expected": f"Not receiving {conflict}",
                "actual": conflict,
            })

    total = len(matched) + len(failed) + len(missing)
    score = round((len(matched) / total) * 100, 1) if total else 0
    if failed:
        status = "NOT_ELIGIBLE"
    elif missing:
        status = "POTENTIALLY_ELIGIBLE"
    else:
        status = "ELIGIBLE"
    return EligibilityResult(status, score, matched, failed, missing)


def _evaluate(actual: Any, operator: str, expected: Any) -> bool | None:
    if operator == "present":
        return actual is not None and actual != ""
    if actual is None or actual == "":
        return None
    if operator == "eq":
        if isinstance(expected, str):
            return str(actual).strip().lower() == expected.strip().lower()
        return actual == expected
    if operator == "in":
        return str(actual).strip().lower() in {str(item).strip().lower() for item in expected}
    if operator == "gte":
        return float(actual) >= float(expected)
    if operator == "lte":
        return float(actual) <= float(expected)
    if operator == "gt":
        return float(actual) > float(expected)
    if operator == "lt":
        return float(actual) < float(expected)
    if operator == "contains":
        return str(expected).lower() in str(actual).lower()
    return False

