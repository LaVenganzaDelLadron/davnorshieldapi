"""Role-based access control helpers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.models.enums import UserRole
from app.models.user import User


def require_role(required_role: UserRole | str) -> Callable[[User], Awaitable[User]]:
    """Create a dependency that enforces a specific role.

    Super admins are allowed to satisfy any non-super-admin role requirement.
    """

    required = required_role if isinstance(required_role, UserRole) else UserRole(required_role)
    allowed_roles = {required}
    if required != UserRole.super_admin:
        allowed_roles.add(UserRole.super_admin)

    async def role_dependency(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return role_dependency
