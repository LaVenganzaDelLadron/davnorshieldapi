"""Pydantic schemas for the CyberShield DN API."""

from app.schemas.alert import AlertResponse
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportScannerResponse,
    ReportUpdate,
)
from app.schemas.scanner import QRScanRequest, SMSScanRequest, ScanResponse, URLScanRequest
from app.schemas.school import SchoolStatsResponse
from app.schemas.user import UserCreate, UserPublic, UserResponse, UserUpdate
from app.schemas.weather import CyberWeatherResponse

__all__ = [
    "AlertResponse",
    "CyberWeatherResponse",
    "LoginRequest",
    "QRScanRequest",
    "RefreshTokenRequest",
    "ReportCreate",
    "ReportResponse",
    "ReportScannerResponse",
    "ReportUpdate",
    "SMSScanRequest",
    "ScanResponse",
    "SchoolStatsResponse",
    "TokenResponse",
    "URLScanRequest",
    "UserCreate",
    "UserPublic",
    "UserResponse",
    "UserUpdate",
]

