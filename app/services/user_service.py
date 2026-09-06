from __future__ import annotations
from typing import Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    """Business logic for user CRUD and listing."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def get_user(self, user_id: UUID) -> User | None:
        """Return a user by UUID."""

        user = await self.users.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return user

    async def list_users(
        self,
        *,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """Return users with pagination and filters."""

        return await self.users.list_users(
            page=page,
            size=size,
            search=search,
            role=role,
            is_active=is_active,
        )

    async def list_users_by_barangay(
        self,
        barangay_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[User], int]:
        """Return users in a barangay."""

        return await self.users.list_users_by_barangay(barangay_id, page=page, size=size)

    async def list_users_by_municipality(
        self,
        municipality_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[User], int]:
        """Return users in a municipality."""

        return await self.users.list_users_by_municipality(
            municipality_id,
            page=page,
            size=size,
        )

    async def update_user(self, user_id: UUID, update_data: dict[str, Any]) -> User:
        """Update a user and guard against duplicate emails."""

        if "email" in update_data and update_data["email"] is not None:
            existing = await self.users.get_user_by_email(str(update_data["email"]))
            if existing is not None and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists.",
                )
            update_data["email"] = str(update_data["email"]).lower()
        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = hash_password(str(update_data.pop("password")))
        updated = await self.users.update_user(user_id, update_data)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return updated

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user."""

        deleted = await self.users.delete_user(user_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return deleted
