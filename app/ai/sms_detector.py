"""SMS scam analysis."""

from __future__ import annotations

from app.config import settings
from app.constants import ThreatCategory
from app.ai.keyword_model import detect_profile
from app.ai.recommendation_engine import generate_recommendations
from app.utils.sms_parser import clean_message, extract_keywords, extract_links, extract_phone_numbers

OTP_KEYWORDS = {"otp", "one-time password", "verification code", "code"}
BANK_KEYWORDS = {"bank", "account", "debit", "credit", "card", "gcash", "maya"}
URGENCY_KEYWORDS = {"urgent", "immediately", "asap", "now", "suspended", "expire"}
PRIZE_KEYWORDS = {"winner", "claim", "prize", "reward", "congratulations", "free"}
AYUDA_KEYWORDS = {"ayuda", "relief", "cash aid", "cash assistance", "dole", "dswd", "gov"}


def detect_sms_scam(message: str) -> dict[str, object]:
    """Analyze an SMS for scam indicators."""

    cleaned = clean_message(message)
    lower = cleaned.lower()
    phone_numbers = extract_phone_numbers(cleaned)
    links = extract_links(cleaned)
    keywords = extract_keywords(cleaned)

    indicators: list[str] = []
    score = 0.0

    if any(keyword in lower for keyword in OTP_KEYWORDS):
        indicators.append("otp_scam")
        score += 15.0
    if any(keyword in lower for keyword in BANK_KEYWORDS):
        indicators.append("bank_impersonation")
        score += 15.0
    if any(keyword in lower for keyword in URGENCY_KEYWORDS):
        indicators.append("urgency_language")
        score += 10.0
    if any(keyword in lower for keyword in PRIZE_KEYWORDS):
        indicators.append("fake_prize")
        score += 10.0
    if any(keyword in lower for keyword in AYUDA_KEYWORDS):
        indicators.append("fake_government_aid")
        score += 12.0
    if "gcash" in lower or "maya" in lower:
        indicators.append("fake_gcash_message")
        score += 14.0
    if links:
        indicators.append("contains_links")
        score += 10.0
    if phone_numbers:
        indicators.append("contains_phone_number")
        score += 6.0

    profile_matches = detect_profile(cleaned)
    if profile_matches:
        indicators.extend(f"profile:{profile}" for profile in profile_matches)
        score += min(len(profile_matches) * 3.0, 12.0)

    score += min(len(keywords) * 0.8, 8.0)
    score = round(min(score, 100.0), 2)

    if score >= settings.THREAT_SCORE_THRESHOLD:
        risk_level = "DANGEROUS"
    elif score >= settings.THREAT_SCORE_THRESHOLD / 2:
        risk_level = "SUSPICIOUS"
    else:
        risk_level = "SAFE"

    return {
        "score": score,
        "risk_level": risk_level,
        "category": ThreatCategory.sms_scam,
        "explanation": "SMS contains scam-like linguistic and structural indicators.",
        "detected_indicators": indicators,
        "phone_numbers": phone_numbers,
        "links": links,
        "keywords": keywords[:20],
        "recommendations": generate_recommendations(ThreatCategory.sms_scam, language="en"),
    }
