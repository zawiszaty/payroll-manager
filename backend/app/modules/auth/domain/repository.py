from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.auth.domain.models import User


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a new user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Update an existing user."""
        pass

    @abstractmethod
    async def list_all(self) -> list[User]:
        """List all users."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists."""
        pass

    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> User | None:
        """Get user by refresh token."""
        pass
