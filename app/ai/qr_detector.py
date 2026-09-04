"""Heuristic QR scam detection."""

from __future__ import annotations

from app.models.enums import ThreatCategory
from app.utils.qr_parser import classify_qr_type, extract_destination
from app.utils.recommendation import get_recommendations_for_category
from app.utils.risk_calculator import calculate_risk_score


def detect_qr_threat(qr_data: str) -> dict[str, object]:
    """Return QR threat detection output."""

    qr_type = classify_qr_type(qr_data)
    destination = extract_destination(qr_data)
    risk_score = calculate_risk_score(
        malicious_url=qr_type == "url",
        suspicious_keywords=1 if qr_type in {"payment", "contact"} else 0,
        suspicious_phone=False,
        duplicate_reports=0,
        outbreak_score=0.0,
        qr_match=True,
    )
    return {
        "risk_score": risk_score,
        "threat_category": ThreatCategory.qr_scam,
        "explanation": f"QR payload classified as {qr_type}: {destination}.",
        "recommendations": get_recommendations_for_category(ThreatCategory.qr_scam),
    }

