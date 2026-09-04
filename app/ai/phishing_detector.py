"""Heuristic phishing detection."""

from __future__ import annotations

from app.models.enums import ThreatCategory
from app.utils.recommendation import get_recommendations_for_category
from app.utils.risk_calculator import calculate_risk_score
from app.utils.url_parser import extract_domain, is_ip_address_url


def detect_phishing(url: str, text_context: str = "") -> dict[str, object]:
    """Return phishing detection output for a URL and optional text context."""

    suspicious_keywords = sum(
        1
        for keyword in ("urgent", "verify", "login", "password", "otp", "account", "click")
        if keyword in text_context.lower() or keyword in url.lower()
    )
    risk_score = calculate_risk_score(
        malicious_url=True,
        suspicious_keywords=suspicious_keywords,
        suspicious_phone=False,
        duplicate_reports=0,
        outbreak_score=0.0,
        qr_match=False,
    )
    if is_ip_address_url(url) or "@" in extract_domain(url):
        risk_score = min(100.0, risk_score + 10.0)
    return {
        "risk_score": risk_score,
        "threat_category": ThreatCategory.phishing,
        "explanation": "URL contains phishing indicators.",
        "recommendations": get_recommendations_for_category(ThreatCategory.phishing),
    }

