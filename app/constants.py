"""Root application enums and shared constants."""

from __future__ import annotations

from enum import Enum

from app.models.enums import AlertLevel, ReportStatus, ThreatCategory, UserRole


class RiskLevel(str, Enum):
    """High-level cyber weather risk levels."""

    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    DANGEROUS = "DANGEROUS"
