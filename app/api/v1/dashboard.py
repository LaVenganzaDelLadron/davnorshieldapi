"""Dashboard routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.dependencies import get_db
from app.models.enums import UserRole
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


async def _dashboard(db: AsyncSession) -> dict[str, object]:
    """Build the dashboard payload once."""

    return await DashboardService(db).generate_dashboard()


@router.get("/lgu", dependencies=[Depends(require_role(UserRole.municipality_admin))])
async def lgu_dashboard(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return the LGU dashboard."""

    return await _dashboard(db)


@router.get("/admin", dependencies=[Depends(require_role(UserRole.municipality_admin))])
async def admin_dashboard(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return the administrative dashboard."""

    return await _dashboard(db)


@router.get("/analytics", dependencies=[Depends(require_role(UserRole.municipality_admin))])
async def analytics(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, object]:
    """Return analytics aggregates."""

    return await _dashboard(db)


@router.get("/top-threats", dependencies=[Depends(require_role(UserRole.municipality_admin))])
async def top_threats(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return top threat categories."""

    return (await _dashboard(db))["top_threat_categories"]


@router.get("/outbreaks", dependencies=[Depends(require_role(UserRole.municipality_admin))])
async def outbreaks(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return active outbreak summaries."""

    return (await _dashboard(db))["active_outbreaks"]
