from __future__ import annotations
from fastapi import APIRouter, status
from app.schemas.scanner import QRScanRequest, SMSScanRequest, ScanResponse, URLScanRequest
from app.services.scanner_service import ScannerService

router = APIRouter(prefix="/scanner", tags=["Scanner"])


@router.post("/url", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_url(payload: URLScanRequest) -> ScanResponse:
    """Scan a URL for phishing indicators."""

    return await ScannerService().scan_url(payload)


@router.post("/sms", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_sms(payload: SMSScanRequest) -> ScanResponse:
    """Scan an SMS message for scam indicators."""

    return await ScannerService().scan_sms(payload)


@router.post("/qr", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_qr(payload: QRScanRequest) -> ScanResponse:
    """Scan a QR payload for scam indicators."""

    return await ScannerService().scan_qr(payload)


@router.post("/text", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_text(payload: dict[str, str]) -> ScanResponse:
    """Analyze free-form text for threat indicators."""

    text = payload.get("text", "")
    return await ScannerService().analyze_text(text)

