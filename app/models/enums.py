"""Shared enumeration types for the CyberShield DN domain."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SAEnum


class UserRole(str, Enum):
    """Application roles used for access control."""

    citizen = "citizen"
    barangay_admin = "barangay_admin"
    municipality_admin = "municipality_admin"
    school_admin = "school_admin"
    super_admin = "super_admin"


class ThreatCategory(str, Enum):
    """Threat classifications inferred from reports and scanner results."""

    phishing = "phishing"
    sms_scam = "sms_scam"
    qr_scam = "qr_scam"
    marketplace_scam = "marketplace_scam"
    fake_job = "fake_job"
    fake_investment = "fake_investment"
    identity_theft = "identity_theft"
    malware = "malware"
    other = "other"
    PHISHING = phishing
    SMS_SCAM = sms_scam
    QR_SCAM = qr_scam
    MARKETPLACE_SCAM = marketplace_scam
    FAKE_JOB = fake_job
    FAKE_INVESTMENT = fake_investment
    IDENTITY_THEFT = identity_theft
    MALWARE = malware
    OTHER = other


class AlertLevel(str, Enum):
    """Severity levels for alerts issued to communities."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    LOW = low
    MEDIUM = medium
    HIGH = high
    CRITICAL = critical


class ReportStatus(str, Enum):
    """Lifecycle states for scam reports."""

    pending = "pending"
    verified = "verified"
    resolved = "resolved"
    rejected = "rejected"
    PENDING = pending
    VERIFIED = verified
    RESOLVED = resolved
    REJECTED = rejected
    investigating = verified
    dismissed = rejected


def _enum_type(enum_cls: type[Enum], name: str) -> SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=True,
        validate_strings=True,
        values_callable=lambda enum_class: [member.value for member in enum_class],
    )


USER_ROLE_ENUM = _enum_type(UserRole, "user_role")
THREAT_CATEGORY_ENUM = _enum_type(ThreatCategory, "threat_category")
ALERT_LEVEL_ENUM = _enum_type(AlertLevel, "alert_level")
REPORT_STATUS_ENUM = _enum_type(ReportStatus, "report_status")

ADMIN_ROLES = frozenset(
    {
        UserRole.barangay_admin,
        UserRole.municipality_admin,
        UserRole.school_admin,
        UserRole.super_admin,
    }
)
