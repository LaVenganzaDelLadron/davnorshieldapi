from __future__ import annotations
from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_admin_dependency, get_db, get_pagination
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _page_payload(items: list[UserResponse], total: int, page: int, size: int) -> dict[str, Any]:
    """Return a standard paginated payload."""

    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/", dependencies=[Depends(get_current_admin_dependency)])
async def list_users(
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
) -> dict[str, Any]:
    """List users with pagination."""

    from app.models.enums import UserRole as ModelUserRole

    selected_role = ModelUserRole(role) if role else None
    items, total = await UserService(db).list_users(
        page=pagination.page,
        size=pagination.size,
        search=search,
        role=selected_role,
        is_active=is_active,
    )
    return _page_payload(
        [UserResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/{user_id}", dependencies=[Depends(get_current_admin_dependency)], response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Return a single user."""

    user = await UserService(db).get_user(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", dependencies=[Depends(get_current_admin_dependency)], response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update a user."""

    user = await UserService(db).update_user(user_id, payload.model_dump(exclude_unset=True))
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", dependencies=[Depends(get_current_admin_dependency)])
async def delete_user(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Delete a user."""

    await UserService(db).delete_user(user_id)
    return {"detail": "User deleted."}


@router.get("/barangay/{barangay_id}", dependencies=[Depends(get_current_admin_dependency)])
async def list_users_by_barangay(
    barangay_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List users assigned to a barangay."""

    items, total = await UserService(db).list_users_by_barangay(
        barangay_id,
        page=pagination.page,
        size=pagination.size,
    )
    return _page_payload(
        [UserResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )


@router.get("/municipality/{municipality_id}", dependencies=[Depends(get_current_admin_dependency)])
async def list_users_by_municipality(
    municipality_id: UUID,
    pagination: Annotated[object, Depends(get_pagination)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """List users assigned to a municipality."""

    items, total = await UserService(db).list_users_by_municipality(
        municipality_id,
        page=pagination.page,
        size=pagination.size,
    )
    return _page_payload(
        [UserResponse.model_validate(item) for item in items],
        total,
        pagination.page,
        pagination.size,
    )
