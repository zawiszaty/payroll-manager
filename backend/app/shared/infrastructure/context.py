"""Request context for storing current user information."""

from contextvars import ContextVar
from uuid import UUID

# Context variable to store current user ID across async contexts
current_user_id: ContextVar[UUID | None] = ContextVar("current_user_id", default=None)


def set_current_user_id(user_id: UUID | None) -> None:
    """Set the current user ID in the context."""
    current_user_id.set(user_id)


def get_current_user_id() -> UUID | None:
    """Get the current user ID from the context."""
    return current_user_id.get()
