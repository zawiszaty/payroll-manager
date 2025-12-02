"""Domain events for audit module"""

from datetime import datetime
from typing import Any
from uuid import UUID

from app.shared.domain.events import DomainEvent


class AuditLogCreatedEvent(DomainEvent):
    """Generic event for creating audit logs"""

    entity_type: str
    entity_id: UUID
    action: str
    employee_id: UUID | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    changed_by: UUID | None
    metadata: dict[str, Any] | None
    occurred_at: datetime
