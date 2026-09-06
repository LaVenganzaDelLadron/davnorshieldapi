from __future__ import annotations
from datetime import date
from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_active_user_dependency, get_db, get_pagination
from app.models.enums import ReportStatus, ThreatCategory
from app.models.user import User
from app.schemas.report import ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Scam Reports"])


def _none_if_blank(value: str | None) -> str | None:
    """Normalize blank form values to None."""

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _page_payload(items: list[ReportResponse], total: int, page: int, size: int) -> dict[str, Any]:
    """Return a standard paginated payload."""

    return {"items": items, "total": total, "page": page, "size": size}


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    current_user: Annotated[User, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
    report_type: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    municipality_id: UUID = Form(...),
    barangay_id: UUID = Form(...),
    suspicious_url: str | None = Form(default=None),
    phone_number: str | None = Form(default=None),
    qr_data: str | None = Form(default=None),
    screenshot: UploadFile | None = File(default=None),
) -> ReportResponse:
    """Submit a scam report."""

    screenshot_bytes = await screenshot.read() if screenshot is not None else None
    service = ReportService(db)
    result = await service.submit_scam_report(
        user_id=current_user.id,
        municipality_id=municipality_id,
        barangay_id=barangay_id,
        report_type=report_type,
        title=title,
        description=description,
        suspicious_url=_none_if_blank(suspicious_url),
        phone_number=_none_if_blank(phone_number),
        qr_data=_none_if_blank(qr_data),
        screenshot_bytes=screenshot_bytes,
        screenshot_filename=screenshot.filename if screenshot is not None else None,
    )
    return ReportResponse.model_validate(result.report)


@router.get("/")
async def list_reports(
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: ThreatCategory | None = Query(default=None),
    status_filter: ReportStatus | None = Query(default=None, alias="status"),
    municipality: UUID | None = Query(default=None),
    barangay: UUID | None = Query(default=None),
    date_filter: date | None = Query(default=None, alias="date"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
) -> dict[str, Any]:
    """List reports with filters and pagination."""

    service = ReportService(db)
    if date_filter is not None and start_date is None and end_date is None:
        start_date = date_filter
        end_date = date_filter
    items, total = await service.list_reports(
        page=pagination.page,
        size=pagination.size,
        threat_category=category,
        status=status_filter,
        municipality_id=municipality,
        barangay_id=barangay,
        start_date=start_date,
        end_date=end_date,
    )
    return _page_payload(
        [ReportResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportResponse:
    """Return a single report."""

    report = await ReportService(db).get_report(report_id)
    return ReportResponse.model_validate(report)


class ReportStatusUpdate(BaseModel):
    """Report status update payload."""

    model_config = ConfigDict(extra="forbid")

    status: ReportStatus


@router.patch("/{report_id}/status", response_model=ReportResponse)
async def update_report_status(
    report_id: UUID,
    payload: ReportStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ReportResponse:
    """Update the status of a report."""

    report = await ReportService(db).update_report_status(report_id, payload.status)
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}")
async def delete_report(
    report_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Delete a report."""

    await ReportService(db).delete_report(report_id)
    return {"detail": "Report deleted."}


@router.get("/barangay/{barangay_id}")
async def list_reports_by_barangay(
    barangay_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List reports by barangay."""

    items, total = await ReportService(db).get_reports_feed(
        page=pagination.page,
        size=pagination.size,
        barangay_id=barangay_id,
    )
    return _page_payload(
        [ReportResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/municipality/{municipality_id}")
async def list_reports_by_municipality(
    municipality_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List reports by municipality."""

    items, total = await ReportService(db).get_reports_feed(
        page=pagination.page,
        size=pagination.size,
        municipality_id=municipality_id,
    )
    return _page_payload(
        [ReportResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )
