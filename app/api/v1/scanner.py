from __future__ import annotations
from collections.abc import AsyncIterator
import logging
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal
from app.schemas.scanner import QRScanRequest, SMSScanRequest, ScanResponse, URLScanRequest
from app.services.scanner_service import ScannerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scanner", tags=["Scanner"])


async def get_scanner_db() -> AsyncIterator[AsyncSession | None]:
    """Make database retrieval optional so heuristic fallback remains available."""

    try:
        async with AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError as exc:
        logger.warning("Scanner database unavailable; continuing without RAG context: %s", exc)
        yield None


@router.post("/url", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_url(payload: URLScanRequest, db: Annotated[AsyncSession | None, Depends(get_scanner_db)]) -> ScanResponse:
    """Scan a URL for phishing indicators."""

    return await ScannerService(db).scan_url(payload)


@router.post("/sms", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_sms(payload: SMSScanRequest, db: Annotated[AsyncSession | None, Depends(get_scanner_db)]) -> ScanResponse:
    """Scan an SMS message for scam indicators."""

    return await ScannerService(db).scan_sms(payload)


@router.post("/qr", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_qr(payload: QRScanRequest, db: Annotated[AsyncSession | None, Depends(get_scanner_db)]) -> ScanResponse:
    """Scan a QR payload for scam indicators."""

    return await ScannerService(db).scan_qr(payload)


@router.post("/text", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_text(payload: dict[str, str], db: Annotated[AsyncSession | None, Depends(get_scanner_db)]) -> ScanResponse:
    """Analyze free-form text for threat indicators."""

    text = payload.get("text", "")
    return await ScannerService(db).analyze_text(text)
