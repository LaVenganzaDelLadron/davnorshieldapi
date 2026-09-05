"""Threat-specific recommendation helpers."""

from __future__ import annotations

from app.models.enums import ThreatCategory

_DEFAULT_RECOMMENDATIONS = [
    "Treat the message cautiously.",
    "Verify the source through a trusted channel.",
    "Report suspicious activity.",
]


def get_recommendations_for_category(category: ThreatCategory | str) -> list[str]:
    """Return safety recommendations for a threat category."""

    category_value = category.value if isinstance(category, ThreatCategory) else str(category)
    category_value = category_value.strip().lower()
    mapping: dict[str, list[str]] = {
        ThreatCategory.phishing.value: [
            "Don't click the link.",
            "Block the sender.",
            "Report the message.",
        ],
        ThreatCategory.sms_scam.value: [
            "Do not reply to unknown numbers.",
            "Verify the sender independently.",
            "Report suspicious SMS content.",
        ],
        ThreatCategory.qr_scam.value: [
            "Verify the merchant.",
            "Don't scan unknown QR codes.",
            "Inspect the destination before opening it.",
        ],
        ThreatCategory.marketplace_scam.value: [
            "Verify the seller.",
            "Avoid advance payment.",
            "Use trusted payment channels.",
        ],
        "job_scam": [
            "Verify the employer independently.",
            "Never pay to apply.",
            "Watch for rushed hiring offers.",
        ],
        "investment_scam": [
            "Be skeptical of guaranteed returns.",
            "Check licenses and registrations.",
            "Avoid pressure to deposit immediately.",
        ],
        "identity_theft": [
            "Protect personal information.",
            "Monitor financial and online accounts.",
            "Report unauthorized account activity.",
        ],
        ThreatCategory.malware.value: [
            "Do not open the attachment.",
            "Run a security scan.",
            "Isolate the affected device.",
        ],
        ThreatCategory.other.value: [
            "Treat the message cautiously.",
            "Verify the source through a trusted channel.",
            "Report suspicious activity.",
        ],
    }
    return mapping.get(category_value, _DEFAULT_RECOMMENDATIONS)
