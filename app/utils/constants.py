"""Shared constants and enums for backend services."""

from __future__ import annotations

from enum import Enum


class ThreatCategory(str, Enum):
    """Threat categories used across scanners, reports, and recommendations."""

    PHISHING = "phishing"
    SMS_SCAM = "sms_scam"
    QR_SCAM = "qr_scam"
    MARKETPLACE_SCAM = "marketplace_scam"
    JOB_SCAM = "job_scam"
    INVESTMENT_SCAM = "investment_scam"
    IDENTITY_THEFT = "identity_theft"
    OTHER = "other"


class AlertLevel(str, Enum):
    """Alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportStatus(str, Enum):
    """Lifecycle states for scam reports."""

    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    RESOLVED = "resolved"


MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
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
    "igacos": [
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

