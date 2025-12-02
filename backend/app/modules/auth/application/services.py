from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.modules.auth.domain.models import User
from app.modules.auth.domain.repository import UserRepository
from app.modules.auth.domain.value_objects import UserRole

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain text password."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active():
            return None
        return user

    @staticmethod
    def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict[str, Any] | None:
        """Decode and verify a JWT access token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    async def get_current_user(self, token: str) -> User | None:
        """Get current user from JWT token."""
        payload = self.decode_access_token(token)
        if payload is None:
            return None

        user_id: str | None = payload.get("sub")
        if user_id is None:
            return None

        try:
            user_uuid = UUID(user_id)
        except ValueError:
            return None

        user = await self.user_repository.get_by_id(user_uuid)
        if user is None or not user.is_active():
            return None

        return user

    async def create_user(
        self,
        email: str,
        password: str,
        role: UserRole = UserRole.ADMIN,
        full_name: str | None = None,
    ) -> User:
        """Create a new user with hashed password."""
        # Check if user already exists
        if await self.user_repository.exists_by_email(email):
            raise ValueError(f"User with email {email} already exists")

        hashed_password = self.hash_password(password)
        user = User.create(
            email=email,
            hashed_password=hashed_password,
            role=role,
            full_name=full_name,
        )
        return await self.user_repository.create(user)

    async def change_password(self, user_id: UUID, new_password: str) -> User:
        """Change user password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        hashed_password = self.hash_password(new_password)
        user.update_password(hashed_password)
        return await self.user_repository.update(user)

    @staticmethod
    def create_refresh_token() -> str:
        """Create a secure refresh token."""
        return token_urlsafe(32)

    async def set_refresh_token(self, user: User) -> tuple[str, User]:
        """Generate and set a refresh token for the user."""
        refresh_token = self.create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        user.set_refresh_token(refresh_token, expires_at)
        updated_user = await self.user_repository.update(user)

        return refresh_token, updated_user

    async def verify_refresh_token(self, refresh_token: str) -> User | None:
        """Verify a refresh token and return the user if valid."""
        user = await self.user_repository.get_by_refresh_token(refresh_token)

        if user and user.is_refresh_token_valid():
            return user

        return None

    async def revoke_refresh_token(self, user: User) -> User:
        """Revoke a user's refresh token (logout)."""
        user.clear_refresh_token()
        return await self.user_repository.update(user)
