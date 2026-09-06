from __future__ import annotations
from collections.abc import Mapping
from uuid import UUID
from sqlalchemy import or_, select
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.base import RepositoryBase


class UserRepository(RepositoryBase):
    """Database operations for users."""

    async def create_user(self, user_data: Mapping[str, object]) -> User:
        """Create and persist a new user."""

        user = User(**self._mapping_data(user_data))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by its UUID."""

        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email address."""

        result = await self.db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    async def update_user(self, user_id: UUID, update_data: Mapping[str, object]) -> User | None:
        """Update a user record and return the refreshed model."""

        user = await self.get_user_by_id(user_id)
        if user is None:
            return None
        for key, value in self._mapping_data(update_data).items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user by UUID."""

        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True

    async def list_users(
        self,
        *,
        page: int = 1,
        size: int = 20,
        search: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[User], int]:
        """List users with pagination and optional filters."""

        stmt = select(User)
        count_stmt = self._count_statement(User)
        filters = []
        if search:
            search_term = f"%{search.lower()}%"
            filters.append(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.phone.ilike(search_term),
                )
            )
        if role is not None:
            filters.append(User.role == role)
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))
        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)
        stmt = stmt.order_by(User.created_at.desc())
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_users_by_barangay(
        self,
        barangay_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[User], int]:
        """List users assigned to a barangay."""

        stmt = select(User).where(User.barangay_id == barangay_id).order_by(User.created_at.desc())
        count_stmt = self._count_statement(User, User.barangay_id == barangay_id)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

    async def list_users_by_municipality(
        self,
        municipality_id: UUID,
        *,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[User], int]:
        """List users assigned to a municipality."""

        stmt = (
            select(User)
            .where(User.municipality_id == municipality_id)
            .order_by(User.created_at.desc())
        )
        count_stmt = self._count_statement(User, User.municipality_id == municipality_id)
        return await self._paginate(stmt, count_stmt, page=page, size=size)

