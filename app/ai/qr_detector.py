"""QR destination analysis."""

from __future__ import annotations

from urllib.parse import urlparse

from app.config import settings
from app.constants import ThreatCategory
from app.ai.phishing_detector import detect_phishing
from app.ai.recommendation_engine import generate_recommendations
from app.utils.qr_parser import classify_qr_type, decode_qr_text, extract_destination


def _classify_destination(destination: str) -> str:
    lower = destination.lower()
    if lower.startswith(("http://", "https://")):
        return "URL QR"
    if lower.startswith("wifi:") or "ssid=" in lower or "wpa" in lower:
        return "WiFi QR"
    if lower.startswith(("tel:", "mailto:", "sms:")) or "contact" in lower:
        return "Contact QR"
    if "gcash" in lower or "maya" in lower or "pay" in lower:
        return "Payment QR"
    return "Text QR"


def analyze_qr(qr_text: str) -> dict[str, object]:
    """Analyze QR payload and return risk analysis."""

    cleaned = decode_qr_text(qr_text)
    qr_type = classify_qr_type(cleaned)
    destination = extract_destination(cleaned)
    detected_indicators: list[str] = [f"qr_type:{qr_type}", f"classification:{_classify_destination(destination)}"]

    if qr_type == "url":
        phishing = detect_phishing(destination, text_context=cleaned)
        detected_indicators.extend(phishing.get("detected_indicators", []))
        score = float(phishing["score"])
        explanation = f"QR points to a URL destination: {phishing['explanation']}"
        category = ThreatCategory.qr_scam
    else:
        score = 20.0 if qr_type in {"payment", "contact"} else 5.0
        explanation = "QR destination does not resolve to a URL, but still deserves caution."
        category = ThreatCategory.qr_scam

    risk_level = (
        "DANGEROUS"
        if score >= settings.THREAT_SCORE_THRESHOLD
        else "SUSPICIOUS"
        if score >= settings.THREAT_SCORE_THRESHOLD / 2
        else "SAFE"
    )
    return {
        "score": round(min(score, 100.0), 2),
        "risk_level": risk_level,
        "category": category,
        "explanation": explanation,
        "detected_indicators": detected_indicators,
        "destination": destination,
        "qr_classification": _classify_destination(destination),
        "recommendations": generate_recommendations(ThreatCategory.qr_scam, language="en"),
    }


def detect_qr_threat(qr_text: str) -> dict[str, object]:
    """Backward-compatible alias for QR analysis."""

    return analyze_qr(qr_text)
