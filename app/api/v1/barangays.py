"""Barangay reference-data routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_role
from app.dependencies import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.location import BarangayCreate, BarangayResponse, BarangayUpdate
from app.services.audit_service import AuditService
from app.services.barangay_service import BarangayService

router = APIRouter(prefix="/barangays", tags=["Barangays"])


def _serialize_barangay(barangay) -> dict[str, object]:
    return {
        "id": str(barangay.id),
        "barangay_name": barangay.barangay_name,
        "municipality_id": str(barangay.municipality_id),
    }


async def _audit(request: Request, db: AsyncSession, user: User, action: str) -> None:
    await AuditService(db).log_admin_action(
        user_id=user.id, action=action, endpoint=request.url.path,
        ip_address=request.client.host if request.client else None,
        device=request.headers.get("user-agent"),
    )


@router.get("/")
async def list_barangays(db: Annotated[AsyncSession, Depends(get_db)]) -> list[dict[str, object]]:
    """Return all barangays."""
    return [_serialize_barangay(item) for item in await BarangayService(db).list_barangays()]


@router.get("/municipality/{municipality_id}")
async def list_barangays_by_municipality(
    municipality_id: UUID, db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict[str, object]]:
    """Return barangays for a municipality."""
    barangays = await BarangayService(db).list_barangays_by_municipality(municipality_id)
    return [_serialize_barangay(item) for item in barangays]


@router.post("/", response_model=BarangayResponse, status_code=status.HTTP_201_CREATED)
async def create_barangay(
    payload: BarangayCreate, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BarangayResponse:
    """Add a barangay to an active Davao del Norte municipality."""
    barangay = await BarangayService(db).create_barangay(payload.model_dump())
    await _audit(request, db, current_user, f"barangay_created:{barangay.id}")
    return BarangayResponse.model_validate(barangay)


@router.patch("/{barangay_id}", response_model=BarangayResponse)
async def update_barangay(
    barangay_id: UUID, payload: BarangayUpdate, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BarangayResponse:
    """Edit a barangay or move it between active local municipalities."""
    barangay = await BarangayService(db).update_barangay(
        barangay_id, payload.model_dump(exclude_unset=True)
    )
    await _audit(request, db, current_user, f"barangay_updated:{barangay.id}")
    return BarangayResponse.model_validate(barangay)


@router.delete("/{barangay_id}")
async def delete_barangay(
    barangay_id: UUID, request: Request,
    current_user: Annotated[User, Depends(require_role(UserRole.super_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Delete an unused barangay (super admin only)."""
    await BarangayService(db).delete_barangay(barangay_id)
    await _audit(request, db, current_user, f"barangay_deleted:{barangay_id}")
    return {"detail": "Barangay deleted."}


@router.get("/{barangay_id}")
async def get_barangay(
    barangay_id: UUID, db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Return a barangay by UUID."""
    return _serialize_barangay(await BarangayService(db).get_barangay(barangay_id))
