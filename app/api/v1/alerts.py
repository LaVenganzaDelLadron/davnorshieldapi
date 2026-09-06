from __future__ import annotations
from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.constants import AlertLevel
from app.core.permissions import require_role
from app.dependencies import get_db, get_pagination
from app.models.enums import UserRole
from app.schemas.alert import AlertResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class BroadcastAlertRequest(BaseModel):
    """Alert broadcast payload."""

    model_config = ConfigDict(extra="forbid")

    threat_pattern_id: UUID
    municipality_id: UUID
    barangay_id: UUID | None = None
    alert_level: AlertLevel = AlertLevel.MEDIUM
    title: str
    message: str


def _page_payload(items: list[AlertResponse], total: int, page: int, size: int) -> dict[str, Any]:
    """Return a standard paginated payload."""

    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/today")
async def today_alerts(db: Annotated[AsyncSession, Depends(get_db)]) -> list[AlertResponse]:
    """Return today's alerts."""

    items, _ = await AlertService(db).list_today_alerts()
    return [AlertResponse.model_validate(item) for item in items]


@router.get("/active")
async def active_alerts(
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return active alerts."""

    items, total = await AlertService(db).list_alerts(
        page=pagination.page,
        size=pagination.size,
        is_active=True,
    )
    return _page_payload(
        [AlertResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/barangay/{barangay_id}")
async def barangay_alerts(
    barangay_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return alerts for a barangay."""

    items, total = await AlertService(db).list_barangay_alerts(
        barangay_id,
        page=pagination.page,
        size=pagination.size,
    )
    return _page_payload(
        [AlertResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/municipality/{municipality_id}")
async def municipality_alerts(
    municipality_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Return alerts for a municipality."""

    items, total = await AlertService(db).list_municipality_alerts(
        municipality_id,
        page=pagination.page,
        size=pagination.size,
    )
    return _page_payload(
        [AlertResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.post(
    "/broadcast",
    dependencies=[Depends(require_role(UserRole.municipality_admin))],
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def broadcast_alert(
    payload: BroadcastAlertRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlertResponse:
    """Broadcast an alert to a municipality or barangay."""

    alert = await AlertService(db).broadcast_alert(
        threat_pattern_id=payload.threat_pattern_id,
        municipality_id=payload.municipality_id,
        barangay_id=payload.barangay_id,
        alert_level=payload.alert_level,
        title=payload.title,
        message=payload.message,
    )
    return AlertResponse.model_validate(alert)

