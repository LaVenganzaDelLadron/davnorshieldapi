"""Shared FastAPI dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user, get_current_admin, get_current_user
from app.database.session import get_db
from app.models.barangay import Barangay
from app.models.municipality import Municipality
from app.repositories.barangay_repository import BarangayRepository
from app.repositories.municipality_repository import MunicipalityRepository
from app.models.user import User


@dataclass(slots=True)
class PaginationParams:
    """Pagination query parameters."""

    page: int
    size: int

    @property
    def offset(self) -> int:
        """Return the SQL offset for the current page."""

        return (self.page - 1) * self.size


async def get_current_user_dependency(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the authenticated user."""

    return user


async def get_current_active_user_dependency(
    user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Return the authenticated, active user."""

    return user


async def get_current_admin_dependency(
    user: Annotated[User, Depends(get_current_admin)],
) -> User:
    """Return the authenticated admin user."""

    return user


def get_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> PaginationParams:
    """Return validated pagination parameters."""

    return PaginationParams(page=page, size=size)


async def get_municipality_dependency(
    municipality_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Municipality:
    """Resolve a municipality by UUID or raise 404."""

    repository = MunicipalityRepository(db)
    municipality = await repository.get_municipality(municipality_id)
    if municipality is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Municipality not found.",
        )
    return municipality


async def get_barangay_dependency(
    barangay_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Barangay:
    """Resolve a barangay by UUID or raise 404."""

    repository = BarangayRepository(db)
    barangay = await repository.get_barangay(barangay_id)
    if barangay is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barangay not found.",
        )
    return barangay

