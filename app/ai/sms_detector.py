"""Heuristic SMS scam detection."""

from __future__ import annotations

from app.models.enums import ThreatCategory
from app.utils.recommendation import get_recommendations_for_category
from app.utils.risk_calculator import calculate_risk_score
from app.utils.sms_parser import extract_keywords, extract_links, extract_phone_numbers


def detect_sms_scam(message: str) -> dict[str, object]:
    """Return SMS scam detection output."""

    keywords = extract_keywords(message)
    links = extract_links(message)
    phones = extract_phone_numbers(message)
    risk_score = calculate_risk_score(
        malicious_url=bool(links),
        suspicious_keywords=len(keywords),
        suspicious_phone=bool(phones),
        duplicate_reports=0,
        outbreak_score=0.0,
        qr_match=False,
    )
    return {
        "risk_score": risk_score,
        "threat_category": ThreatCategory.sms_scam,
        "explanation": "SMS contains scam-like patterns.",
        "recommendations": get_recommendations_for_category(ThreatCategory.sms_scam),
    }

