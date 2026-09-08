from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole


class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    role: UserRole = UserRole.citizen
    municipality_id: UUID | None = None
    barangay_id: UUID | None = None
    is_active: bool = True


class UserCreate(UserBase):
    """Payload for creating a user."""

    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: UserRole | None = None
    municipality_id: UUID | None = None
    barangay_id: UUID | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    full_name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    municipality_id: UUID | None
    barangay_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: UUID
    full_name: str
    role: UserRole
    municipality_id: UUID | None
    barangay_id: UUID | None
    is_active: bool
    created_at: datetime
