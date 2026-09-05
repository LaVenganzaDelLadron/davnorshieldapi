"""Unified AI threat classification entry point."""

from __future__ import annotations

from dataclasses import dataclass

from app.ai.phishing_detector import detect_phishing
from app.ai.qr_detector import analyze_qr
from app.ai.sms_detector import detect_sms_scam
from app.ai.recommendation_engine import generate_recommendations
from app.constants import ThreatCategory
from app.utils.sms_parser import extract_links


@dataclass(slots=True)
class ThreatClassification:
    """Unified result returned by the classifier."""

    score: float
    risk_level: str
    category: ThreatCategory
    explanation: str
    detected_indicators: list[str]
    recommendations: list[str]


def classify_threat(*, url: str | None = None, sms: str | None = None, qr: str | None = None, text: str | None = None) -> ThreatClassification:
    """Dispatch to the specialized detector based on the provided input."""

    if url:
        result = detect_phishing(url, text_context=text or "")
    elif sms:
        result = detect_sms_scam(sms)
    elif qr:
        result = analyze_qr(qr)
    elif text:
        text_links = extract_links(text)
        if text_links:
            result = detect_phishing(text_links[0], text_context=text)
        else:
            result = detect_sms_scam(text)
    else:
        result = {
            "score": 0.0,
            "risk_level": "SAFE",
            "category": ThreatCategory.other,
            "explanation": "No input provided.",
            "detected_indicators": [],
            "recommendations": generate_recommendations(ThreatCategory.other),
        }
    return ThreatClassification(
        score=float(result["score"]),
        risk_level=str(result["risk_level"]),
        category=result["category"],
        explanation=str(result["explanation"]),
        detected_indicators=list(result.get("detected_indicators", [])),
        recommendations=list(result.get("recommendations", generate_recommendations(result["category"]))),
    )
