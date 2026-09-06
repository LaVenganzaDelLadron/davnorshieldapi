from __future__ import annotations
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str

