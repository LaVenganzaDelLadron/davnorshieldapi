"""Request and response schemas for Davao del Norte reference locations."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MunicipalityCreate(BaseModel):
    """Payload for adding a municipality or city."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    municipality_name: str = Field(min_length=1, max_length=255)
    province: str = Field(min_length=1, max_length=255)


class MunicipalityUpdate(BaseModel):
    """Payload for editing a municipality or restoring a soft-deleted one."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    municipality_name: str | None = Field(default=None, min_length=1, max_length=255)
    province: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None


class MunicipalityResponse(BaseModel):
    """Public municipality representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    municipality_name: str
    province: str
    is_active: bool


class BarangayCreate(BaseModel):
    """Payload for adding a barangay to an active municipality."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    barangay_name: str = Field(min_length=1, max_length=255)
    municipality_id: UUID


class BarangayUpdate(BaseModel):
    """Payload for editing a barangay or moving it to another municipality."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    barangay_name: str | None = Field(default=None, min_length=1, max_length=255)
    municipality_id: UUID | None = None


class BarangayResponse(BaseModel):
    """Public barangay representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    barangay_name: str
    municipality_id: UUID
