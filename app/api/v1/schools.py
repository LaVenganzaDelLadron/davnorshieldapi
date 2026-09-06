from __future__ import annotations
from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_role
from app.dependencies import get_db, get_pagination
from app.models.enums import UserRole
from app.schemas.school import SchoolStatsResponse
from app.services.school_service import SchoolService

router = APIRouter(prefix="/schools", tags=["Schools"])


class AwarenessScoreUpdate(BaseModel):
    """Payload for updating a school's awareness score."""

    model_config = ConfigDict(extra="forbid")

    school_id: UUID
    awareness_score: float = Field(ge=0.0, le=100.0)


def _serialize_school(school) -> SchoolStatsResponse:
    """Serialize a school ORM object."""

    return SchoolStatsResponse.model_validate(school)


@router.get("/", dependencies=[Depends(require_role(UserRole.school_admin))])
async def list_schools(
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
    municipality_id: UUID | None = None,
) -> dict[str, Any]:
    """Return school records."""

    schools = await SchoolService(db).list_schools(municipality_id=municipality_id)
    payload = [_serialize_school(school) for school in schools]
    start = (pagination.page - 1) * pagination.size
    end = start + pagination.size
    return {
        "items": payload[start:end],
        "total": len(payload),
        "page": pagination.page,
        "size": pagination.size,
    }


@router.get("/{school_id}", dependencies=[Depends(require_role(UserRole.school_admin))], response_model=SchoolStatsResponse)
async def get_school(
    school_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SchoolStatsResponse:
    """Return a school by UUID."""

    school = await SchoolService(db).get_school(school_id)
    return _serialize_school(school)


@router.get("/stats", dependencies=[Depends(require_role(UserRole.school_admin))])
async def school_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    municipality_id: UUID | None = None,
) -> dict[str, Any]:
    """Return school statistics for the dashboard."""

    service = SchoolService(db)
    return {
        "phishing": await service.phishing_statistics(municipality_id=municipality_id),
        "reports": await service.reports_statistics(municipality_id=municipality_id),
    }


@router.patch("/awareness-score", dependencies=[Depends(require_role(UserRole.school_admin))], response_model=SchoolStatsResponse)
async def update_awareness_score(
    payload: AwarenessScoreUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SchoolStatsResponse:
    """Update a school's awareness score."""

    school = await SchoolService(db).update_awareness_score(payload.school_id, payload.awareness_score)
    return _serialize_school(school)
