from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
os.environ.setdefault("DATABASE_HOST", "localhost")
os.environ.setdefault("DATABASE_USER", "user")
os.environ.setdefault("DATABASE_PASSWORD", "pass")
os.environ.setdefault("DATABASE_NAME", "db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("API_V1_PREFIX", "/api/v1")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.models.enums import ThreatCategory
from app.schemas.scanner import SMSScanRequest
from app.services.scanner_service import ScannerService


def test_normalize_scan_result_accepts_structured_rag_output() -> None:
    result = ScannerService._normalize_scan_result(
        {
            "risk_score": 82,
            "risk_level": "DANGEROUS",
            "category": "phishing",
            "explanation": "The artifact matches known phishing behavior.",
            "recommendations": ["Do not open the link."],
        }
    )

    assert result.risk_score == 82
    assert result.threat_category is ThreatCategory.phishing
    assert result.recommendations == ["Do not open the link."]


@pytest.mark.asyncio
async def test_scanner_falls_back_when_rag_is_not_configured() -> None:
    result = await ScannerService().scan_sms(
        SMSScanRequest(message="Your account is suspended. Verify your OTP now.")
    )

    assert result.threat_category is ThreatCategory.sms_scam
    assert result.risk_score > 0
