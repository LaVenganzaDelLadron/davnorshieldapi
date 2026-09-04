"""Risk scoring helpers."""

from __future__ import annotations


def calculate_risk_score(
    *,
    malicious_url: bool = False,
    suspicious_keywords: int = 0,
    duplicate_reports: int = 0,
    outbreak_score: float = 0.0,
    suspicious_phone: bool = False,
    qr_match: bool = False,
) -> float:
    """Calculate a bounded risk score from detection signals."""

    score = 0.0
    if malicious_url:
        score += 35.0
    if suspicious_phone:
        score += 15.0
    if qr_match:
        score += 20.0
    score += min(suspicious_keywords * 4.0, 20.0)
    score += min(duplicate_reports * 6.0, 15.0)
    score += min(outbreak_score * 0.5, 20.0)
    return round(max(0.0, min(score, 100.0)), 2)


def calculate_confidence_score(
    *,
    evidence_points: int,
    corroborating_reports: int = 0,
    outbreak_score: float = 0.0,
) -> float:
    """Calculate a confidence score for a threat pattern."""

    score = min(evidence_points * 12.0, 60.0)
    score += min(corroborating_reports * 8.0, 30.0)
    score += min(outbreak_score * 0.4, 10.0)
    return round(max(0.0, min(score, 100.0)), 2)

