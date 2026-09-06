from __future__ import annotations
from dataclasses import dataclass
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


@dataclass(slots=True)
class AuthResult:
    """Combined user and token response for auth flows."""

    user: User
    token: TokenResponse


class AuthService:
    """Business logic for registration and authentication."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    def generate_access_token(self, user: User) -> TokenResponse:
        """Create a bearer token response for a user."""

        access_token = create_access_token(subject=str(user.id), role=user.role)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def register_user(self, user_in: UserCreate) -> AuthResult:
        """Register a new user after validating email uniqueness."""

        existing = await self.users.get_user_by_email(str(user_in.email))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        user = await self.users.create_user(
            {
                "full_name": user_in.full_name,
                "email": str(user_in.email).lower(),
                "phone": user_in.phone,
                "password_hash": hash_password(user_in.password),
                "role": user_in.role,
                "municipality_id": user_in.municipality_id,
                "barangay_id": user_in.barangay_id,
                "is_active": user_in.is_active,
            }
        )
        token = self.generate_access_token(user)
        return AuthResult(user=user, token=token)

    async def authenticate_user(self, credentials: LoginRequest) -> AuthResult:
        """Authenticate a user with email and password."""

        user = await self.users.get_user_by_email(str(credentials.email))
        if user is None or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )
        return AuthResult(user=user, token=self.generate_access_token(user))

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> User:
        """Change a user's password after verifying the old password."""

        user = await self.users.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        updated_user = await self.users.update_user(
            user_id,
            {"password_hash": hash_password(new_password)},
        )
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return updated_user

    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user account."""

        updated_user = await self.users.update_user(user_id, {"is_active": False})
        if updated_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        return updated_user
