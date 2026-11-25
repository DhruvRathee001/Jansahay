import re
from collections import Counter

from .models import CitizenProfile, Scheme
from .rules import evaluate_scheme


STOPWORDS = {"the", "and", "for", "with", "want", "need", "help", "mujhe", "hai", "ke", "ki", "ka", "mein", "main"}
SYNONYMS = {
    "farmer": {"farmer", "farming", "agriculture", "kisan", "खेती"},
    "education": {"education", "school", "college", "student", "scholarship", "padhai", "study"},
    "healthcare": {"health", "hospital", "treatment", "medical", "healthcare", "ilaaj"},
    "housing": {"house", "housing", "home", "awas", "ghar", "rent"},
    "employment": {"job", "employment", "business", "vendor", "loan", "work", "rozgar"},
    "senior": {"senior", "old", "elderly", "pension", "vriddh", "age"},
}


def tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-Z0-9]+", value.lower()) if token not in STOPWORDS}


def recommend(query: str, schemes: list[Scheme], profile: CitizenProfile | None, limit: int = 6) -> list[dict]:
    query_tokens = tokenize(query)
    expanded = set(query_tokens)
    for group in SYNONYMS.values():
        if query_tokens & group:
            expanded |= group

    recommendations = []
    for scheme in schemes:
        text = " ".join([scheme.name, scheme.category, scheme.summary, scheme.benefits, scheme.department]).lower()
        scheme_tokens = tokenize(text)
        overlap = len(expanded & scheme_tokens)
        category_bonus = 0
        if scheme.category.lower() in query.lower():
            category_bonus = 3
        result = evaluate_scheme(scheme, profile)
        eligibility_bonus = {"ELIGIBLE": 3, "POTENTIALLY_ELIGIBLE": 1, "NOT_ELIGIBLE": 0}[result.status]
        raw = overlap * 10 + category_bonus * 5 + eligibility_bonus * 4
        if raw == 0:
            continue
        recommendations.append(
            {
                "scheme": scheme,
                "relevance_score": min(99, round(50 + raw * 2.5, 1)),
                "eligibility": result.status,
                "eligibility_score": result.score,
                "why": _why(scheme, result, overlap),
            }
        )
    recommendations.sort(key=lambda item: (item["relevance_score"], item["eligibility_score"]), reverse=True)
    return recommendations[:limit]


def _why(scheme: Scheme, result, overlap: int) -> str:
    reasons = []
    if overlap:
        reasons.append(f"your request matches the {scheme.category.lower()} category")
    if result.status == "ELIGIBLE":
        reasons.append("your saved profile satisfies the available conditions")
    elif result.status == "POTENTIALLY_ELIGIBLE":
        reasons.append("the scheme looks relevant but some profile information is missing")
    else:
        reasons.append("the scheme is relevant to your request, although one or more conditions currently fail")
    return "; ".join(reasons).capitalize() + "."

