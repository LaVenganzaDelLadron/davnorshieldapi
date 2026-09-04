"""Import ORM models so SQLAlchemy registers mappings on package import."""

from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.barangay import Barangay
from app.models.cyber_weather import CyberWeather
from app.models.enums import (
    ALERT_LEVEL_ENUM,
    ADMIN_ROLES,
    REPORT_STATUS_ENUM,
    THREAT_CATEGORY_ENUM,
    USER_ROLE_ENUM,
    AlertLevel,
    ReportStatus,
    ThreatCategory,
    UserRole,
)
from app.models.municipality import Municipality
from app.models.notification import Notification
from app.models.scam_report import ScamReport
from app.models.school import School
from app.models.threat_pattern import ThreatPattern
from app.models.user import User

__all__ = [
    "Alert",
    "ALERT_LEVEL_ENUM",
    "ADMIN_ROLES",
    "AuditLog",
    "Barangay",
    "CyberWeather",
    "AlertLevel",
    "Municipality",
    "Notification",
    "ReportStatus",
    "REPORT_STATUS_ENUM",
    "ScamReport",
    "School",
    "THREAT_CATEGORY_ENUM",
    "ThreatCategory",
    "ThreatPattern",
    "USER_ROLE_ENUM",
    "User",
    "UserRole",
]
