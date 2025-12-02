from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.auth.application.services import AuthenticationService
from app.modules.auth.domain.models import User
from app.modules.auth.infrastructure.repository import SqlAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SqlAlchemyUserRepository:
    """Get user repository instance."""
    return SqlAlchemyUserRepository(session)


async def get_auth_service(
    repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> AuthenticationService:
    """Get authentication service instance."""
    return AuthenticationService(repository)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await auth_service.get_current_user(token)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Get current active user."""
    if not current_user.is_active():
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Optional: get user ID or None (for endpoints that work with or without auth)
async def get_optional_current_user(
    token: str | None = Depends(oauth2_scheme_optional),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> User | None:
    """Get current user if authenticated, None otherwise."""
    if token is None:
        return None
    return await auth_service.get_current_user(token)
