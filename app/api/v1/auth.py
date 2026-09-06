from __future__ import annotations
from typing import Annotated
from datetime import UTC, datetime
from jose import JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_current_active_user_dependency, get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserPublic, UserResponse
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService
from app.core.auth import oauth2_scheme
from app.core.security import decode_access_token
from app.models.revoked_token import RevokedToken

router = APIRouter(prefix="/auth", tags=["Authentication"])


class ChangePasswordRequest(BaseModel):
    """Password change request payload."""

    model_config = ConfigDict(extra="forbid")

    current_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class AuthResponse(BaseModel):
    """Authentication response payload."""

    user: UserPublic
    token: TokenResponse


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Register a new citizen or administrative account."""

    result = await AuthService(db).register_user(payload)
    return AuthResponse(user=UserPublic.model_validate(result.user), token=result.token)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthResponse:
    """Authenticate a user and issue a bearer token."""

    result = await AuthService(db).authenticate_user(payload)
    await AuditService(db).log_login(user_id=result.user.id)
    return AuthResponse(user=UserPublic.model_validate(result.user), token=result.token)


@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    _current_user: Annotated[object, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Revoke the current access token until its natural expiration."""

    try:
        payload = decode_access_token(token)
        jti = str(payload["jti"])
        expires_at = datetime.fromtimestamp(float(payload["exp"]), tz=UTC)
    except (JWTError, KeyError, TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error

    existing = await db.scalar(
        select(RevokedToken).where(RevokedToken.jti == jti)
    )
    if existing is None:
        db.add(RevokedToken(jti=jti, expires_at=expires_at))
        await db.commit()

    return {"detail": "Successfully logged out."}


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[object, Depends(get_current_active_user_dependency)],
) -> UserResponse:
    """Return the authenticated user profile."""

    return UserResponse.model_validate(current_user)


@router.put("/change-password", response_model=UserPublic)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[object, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPublic:
    """Change the current user's password."""

    user = await AuthService(db).change_password(
        user_id=current_user.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return UserPublic.model_validate(user)


@router.delete("/deactivate-account")
async def deactivate_account(
    current_user: Annotated[object, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Deactivate the authenticated account."""

    await AuthService(db).deactivate_user(current_user.id)
    return {"detail": "Account deactivated."}
