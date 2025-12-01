from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.value_objects import AuditAction, EntityType


class AuditLogRepository(ABC):
    @abstractmethod
    async def save(self, audit_log: AuditLog) -> AuditLog:
        pass

    @abstractmethod
    async def get_by_id(self, audit_id: UUID) -> AuditLog | None:
        pass

    @abstractmethod
    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: EntityType | None = None,
        action: AuditAction | None = None,
    ) -> list[AuditLog]:
        pass

    @abstractmethod
    async def get_by_entity(
        self, entity_type: EntityType, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        pass

    @abstractmethod
    async def get_by_employee(
        self, employee_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        pass

    @abstractmethod
    async def get_timeline(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: EntityType | None = None,
        employee_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[AuditLog]:
        pass
