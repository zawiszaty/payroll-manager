from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.auth.domain.value_objects import UserRole, UserStatus


@dataclass
class User:
    email: str
    hashed_password: str
    role: UserRole
    id: UUID = field(default_factory=uuid4)
    status: UserStatus = UserStatus.ACTIVE
    full_name: str | None = None
    refresh_token: str | None = None
    refresh_token_expires_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def create(
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.USER,
        full_name: str | None = None,
    ) -> "User":
        """Create a new user with least-privilege default role (USER)."""
        return User(
            email=email,
            hashed_password=hashed_password,
            role=role,
            full_name=full_name,
        )

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.status = UserStatus.INACTIVE
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate the user account."""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.now(UTC)

    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE

    def update_password(self, hashed_password: str) -> None:
        """Update user password."""
        self.hashed_password = hashed_password
        self.updated_at = datetime.now(UTC)

    def set_refresh_token(self, token: str, expires_at: datetime) -> None:
        """Set refresh token and expiration."""
        self.refresh_token = token
        self.refresh_token_expires_at = expires_at
        self.updated_at = datetime.now(UTC)

    def clear_refresh_token(self) -> None:
        """Clear refresh token (logout)."""
        self.refresh_token = None
        self.refresh_token_expires_at = None
        self.updated_at = datetime.now(UTC)

    def is_refresh_token_valid(self) -> bool:
        """Check if refresh token is still valid."""
        if not self.refresh_token or not self.refresh_token_expires_at:
            return False
        return datetime.now(UTC) < self.refresh_token_expires_at
