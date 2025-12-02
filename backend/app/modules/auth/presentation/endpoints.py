from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.modules.auth.application.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.application.services import AuthenticationService
from app.modules.auth.domain.models import User
from app.modules.auth.infrastructure.dependencies import (
    get_auth_service,
    get_current_active_user,
)

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """
    OAuth2 compatible token login.

    Use email as username in the OAuth2 password flow.
    Returns both access token and refresh token.
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthenticationService.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )

    # Create and set refresh token
    refresh_token, _ = await auth_service.set_refresh_token(user)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Refresh access token using a valid refresh token.

    The refresh token must be valid and not expired.
    Returns a new access token and refresh token.
    """
    user = await auth_service.verify_refresh_token(request.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthenticationService.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )

    # Create new refresh token
    refresh_token, _ = await auth_service.set_refresh_token(user)
    await session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Logout the current user by revoking their refresh token.
    """
    await auth_service.revoke_refresh_token(current_user)
    await session.commit()
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_active_user)]):
    """Get current authenticated user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        status=current_user.status,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )
