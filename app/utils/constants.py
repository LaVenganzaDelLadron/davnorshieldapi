"""Shared constants for backend services."""

from __future__ import annotations

from app.constants import AlertLevel, ReportStatus, ThreatCategory, UserRole


ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
OUTBREAK_WINDOW_HOURS = 24
DEFAULT_OUTBREAK_THRESHOLD = 10

DAVAO_DEL_NORTE_MUNICIPALITIES: dict[str, list[str]] = {
    "tagum city": [
        "apokon",
        "bincungan",
        "canocotan",
        "magugpo pablacion",
        "visayan village",
    ],
    "island garden city of samal": [
        "san agustin",
        "peñaplata",
        "tagbaobo",
    ],
    "braulio e. dujali": [
        "cabayangan",
        "mabuhay",
        "new casay",
    ],
    "carmen": [
        "mabaus",
        "ising",
        "salvacion",
    ],
    "kapalong": [
        "florida",
        "maniki",
        "semong",
    ],
    "new corella": [
        "cabidianan",
        "mambing",
        "san roque",
    ],
    "san isidro": [
        "sawata",
        "sagayen",
        "tiburcia",
    ],
    "santo tomas": [
        "kapatagan",
        "kimamon",
        "new visayas",
    ],
    "talaingod": [
        "dagohoy",
        "palma gil",
        "sto. nino",
    ],
}

THREAT_CATEGORIES = (
    ThreatCategory.phishing,
    ThreatCategory.sms_scam,
    ThreatCategory.qr_scam,
    ThreatCategory.marketplace_scam,
    ThreatCategory.fake_job,
    ThreatCategory.fake_investment,
    ThreatCategory.identity_theft,
    ThreatCategory.malware,
    ThreatCategory.other,
)
