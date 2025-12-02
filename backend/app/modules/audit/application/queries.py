from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.audit.domain.value_objects import AuditAction, EntityType


@dataclass
class GetAuditLogQuery:
    audit_id: UUID


@dataclass
class ListAuditLogsQuery:
    skip: int = 0
    limit: int = 100
    entity_type: EntityType | None = None
    action: AuditAction | None = None


@dataclass
class GetAuditLogsByEntityQuery:
    entity_type: EntityType
    entity_id: UUID
    skip: int = 0
    limit: int = 100


@dataclass
class GetAuditLogsByEmployeeQuery:
    employee_id: UUID
    skip: int = 0
    limit: int = 100


@dataclass
class GetAuditTimelineQuery:
    skip: int = 0
    limit: int = 100
    entity_type: EntityType | None = None
    employee_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
