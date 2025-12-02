from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.modules.auth.domain.value_objects import UserRole, UserStatus


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until access token expires


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    status: UserStatus
    full_name: str | None
    created_at: datetime
    updated_at: datetime


class CreateUserCommand(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    full_name: str | None = None
