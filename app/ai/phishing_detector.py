"""Phishing scoring and indicator extraction."""

from __future__ import annotations

from urllib.parse import urlparse

from app.config import settings
from app.constants import ThreatCategory
from app.ai.keyword_model import detect_profile
from app.ai.recommendation_engine import generate_recommendations
from app.utils.risk_calculator import calculate_risk_score
from app.utils.url_parser import extract_domain, is_ip_address_url

SUSPICIOUS_TLDS = {
    ".zip",
    ".xyz",
    ".top",
    ".click",
    ".country",
    ".kim",
    ".work",
    ".gq",
    ".tk",
}

URL_SHORTENERS = {
    "bit.ly",
    "t.co",
    "tinyurl.com",
    "goo.su",
    "cutt.ly",
    "rebrand.ly",
}

BRAND_KEYWORDS = {
    "gcash": "gcash",
    "bdo": "bdo",
    "bpi": "bpi",
    "maya": "maya",
    "unionbank": "unionbank",
    "paypal": "paypal",
    "facebook": "facebook",
    "google": "google",
    "microsoft": "microsoft",
}

SUSPICIOUS_KEYWORDS = {
    "urgent",
    "verify",
    "login",
    "password",
    "otp",
    "account",
    "click",
    "secure",
    "limited",
    "suspended",
    "reward",
    "claim",
}


def _has_https_issue(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme.lower() != "https"


def _detect_tld(url: str) -> str:
    host = extract_domain(url)
    return "." + host.split(".")[-1] if "." in host else ""


def detect_phishing(url: str, text_context: str = "") -> dict[str, object]:
    """Score a URL for phishing indicators."""

    lower_url = url.lower()
    lower_text = text_context.lower()
    indicators: list[str] = []
    score = 0.0

    tld = _detect_tld(url)
    if tld in SUSPICIOUS_TLDS:
        indicators.append(f"suspicious_tld:{tld}")
        score += 15.0

    if is_ip_address_url(url):
        indicators.append("ip_address_url")
        score += 20.0

    domain = extract_domain(url)
    if domain in URL_SHORTENERS:
        indicators.append("url_shortener")
        score += 18.0

    if _has_https_issue(url):
        indicators.append("non_https")
        score += 10.0

    for brand, keyword in BRAND_KEYWORDS.items():
        if brand in lower_url or brand in lower_text:
            indicators.append(f"brand_impersonation:{keyword}")
            score += 12.0

    matched_keywords = [keyword for keyword in SUSPICIOUS_KEYWORDS if keyword in lower_url or keyword in lower_text]
    if matched_keywords:
        indicators.extend(f"keyword:{keyword}" for keyword in matched_keywords)
        score += min(len(matched_keywords) * 5.0, 25.0)

    profile_matches = detect_profile(f"{url} {text_context}")
    if profile_matches:
        indicators.extend(f"profile:{profile}" for profile in profile_matches)
        score += min(len(profile_matches) * 3.0, 10.0)

    score = calculate_risk_score(
        malicious_url=True,
        suspicious_keywords=len(matched_keywords),
        duplicate_reports=0,
        outbreak_score=0.0,
        suspicious_phone=False,
        qr_match=False,
    ) + min(score, 20.0)
    score = round(min(score, 100.0), 2)

    if score >= settings.THREAT_SCORE_THRESHOLD:
        explanation = "High-confidence phishing indicators detected."
    elif score >= settings.THREAT_SCORE_THRESHOLD / 2:
        explanation = "Moderate phishing risk detected."
    else:
        explanation = "Low phishing indicators detected."

    return {
        "score": score,
        "risk_level": (
            "DANGEROUS"
            if score >= settings.THREAT_SCORE_THRESHOLD
            else "SUSPICIOUS"
            if score >= settings.THREAT_SCORE_THRESHOLD / 2
            else "SAFE"
        ),
        "category": ThreatCategory.phishing,
        "explanation": explanation,
        "detected_indicators": indicators,
    }
