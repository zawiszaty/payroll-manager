from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.audit.domain.models import AuditLog


class AuditLogResponse(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    employee_id: UUID | None
    action: str
    old_values: dict | None
    new_values: dict | None
    changed_by: UUID | None
    metadata: dict
    occurred_at: datetime
    created_at: datetime

    @classmethod
    def from_domain(cls, audit_log: AuditLog) -> "AuditLogResponse":
        return cls(
            id=audit_log.id,
            entity_type=audit_log.entity_type.value,
            entity_id=audit_log.entity_id,
            employee_id=audit_log.employee_id,
            action=audit_log.action.value,
            old_values=audit_log.old_values,
            new_values=audit_log.new_values,
            changed_by=audit_log.changed_by,
            metadata=audit_log.metadata,
            occurred_at=audit_log.occurred_at,
            created_at=audit_log.created_at,
        )


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    skip: int
    limit: int
