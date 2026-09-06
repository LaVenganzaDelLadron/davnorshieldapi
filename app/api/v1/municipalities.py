from __future__ import annotations
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_role
from app.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.location import MunicipalityCreate, MunicipalityResponse, MunicipalityUpdate
from app.services.audit_service import AuditService
from app.services.municipality_service import MunicipalityService

router = APIRouter(prefix="/municipalities", tags=["Municipalities"])


def _serialize_municipality(municipality) -> dict[str, object]:
    return {
        "id": str(municipality.id),
        "municipality_name": municipality.municipality_name,
        "province": municipality.province,
        "is_active": municipality.is_active,
    }


async def _audit(request: Request, db: AsyncSession, user: User, action: str) -> None:
    await AuditService(db).log_admin_action(
        user_id=user.id, action=action, endpoint=request.url.path,
        ip_address=request.client.host if request.client else None,
        device=request.headers.get("user-agent"),
    )


@router.get("/")
async def list_municipalities(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return active municipalities."""
    return [_serialize_municipality(item) for item in await MunicipalityService(db).list_municipalities()]


@router.get("/summary")
async def municipality_summary(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return municipality summary statistics."""
    return await MunicipalityService(db).get_summary()


@router.post("/", response_model=MunicipalityResponse, status_code=status.HTTP_201_CREATED)
async def create_municipality(
    payload: MunicipalityCreate, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MunicipalityResponse:
    """Add a Davao del Norte municipality or city (super admin only)."""
    municipality = await MunicipalityService(db).create_municipality(payload.model_dump())
    await _audit(request, db, current_user, f"municipality_created:{municipality.id}")
    return MunicipalityResponse.model_validate(municipality)


@router.patch("/{municipality_id}", response_model=MunicipalityResponse)
async def update_municipality(
    municipality_id: UUID, payload: MunicipalityUpdate, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MunicipalityResponse:
    """Edit or restore a municipality (super admin only)."""
    municipality = await MunicipalityService(db).update_municipality(
        municipality_id, payload.model_dump(exclude_unset=True)
    )
    await _audit(request, db, current_user, f"municipality_updated:{municipality.id}")
    return MunicipalityResponse.model_validate(municipality)


@router.delete("/{municipality_id}")
async def delete_municipality(
    municipality_id: UUID, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Soft-delete a municipality without removing related operational data."""
    municipality = await MunicipalityService(db).deactivate_municipality(municipality_id)
    await _audit(request, db, current_user, f"municipality_deactivated:{municipality.id}")
    return {"detail": "Municipality deactivated."}


@router.get("/{municipality_id}")
async def get_municipality(
    municipality_id: UUID, db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Return one active municipality."""
    return _serialize_municipality(await MunicipalityService(db).get_municipality(municipality_id))
