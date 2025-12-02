from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.modules.auth.domain.value_objects import UserRole, UserStatus


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=True),
        nullable=False,
        default=UserRole.ADMIN,
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status", create_type=True),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    refresh_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def to_domain(self):
        from app.modules.auth.domain.models import User

        return User(
            id=self.id,
            email=self.email,
            hashed_password=self.hashed_password,
            role=self.role,
            status=self.status,
            full_name=self.full_name,
            refresh_token=self.refresh_token,
            refresh_token_expires_at=self.refresh_token_expires_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_domain(user):
        return UserModel(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            status=user.status,
            full_name=user.full_name,
            refresh_token=user.refresh_token,
            refresh_token_expires_at=user.refresh_token_expires_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
