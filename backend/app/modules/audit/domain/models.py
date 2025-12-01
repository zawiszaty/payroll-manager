from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.audit.domain.value_objects import AuditAction, EntityType


@dataclass
class AuditLog:
    entity_type: EntityType
    entity_id: UUID
    action: AuditAction
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    changed_by: UUID | None = None
    metadata: dict = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @staticmethod
    def create(
        entity_type: EntityType,
        entity_id: UUID,
        action: AuditAction,
        employee_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        changed_by: UUID | None = None,
        metadata: dict | None = None,
        occurred_at: datetime | None = None,
    ) -> "AuditLog":
        return AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            employee_id=employee_id,
            old_values=old_values,
            new_values=new_values,
            changed_by=changed_by,
            metadata=metadata or {},
            occurred_at=occurred_at or datetime.now(UTC),
        )
