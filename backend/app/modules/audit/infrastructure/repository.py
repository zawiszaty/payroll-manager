from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.domain.models import AuditLog
from app.modules.audit.domain.repository import AuditLogRepository
from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.models import AuditLogORM


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: AuditLogORM) -> AuditLog:
        return AuditLog(
            id=orm.id,
            entity_type=orm.entity_type,
            entity_id=orm.entity_id,
            employee_id=orm.employee_id,
            action=orm.action,
            old_values=orm.old_values,
            new_values=orm.new_values,
            changed_by=orm.changed_by,
            metadata=orm.event_metadata,
            occurred_at=orm.occurred_at,
            created_at=orm.created_at,
        )

    def _to_orm(self, audit_log: AuditLog) -> AuditLogORM:
        return AuditLogORM(
            id=audit_log.id,
            entity_type=audit_log.entity_type,
            entity_id=audit_log.entity_id,
            employee_id=audit_log.employee_id,
            action=audit_log.action,
            old_values=audit_log.old_values,
            new_values=audit_log.new_values,
            changed_by=audit_log.changed_by,
            event_metadata=audit_log.metadata,
            occurred_at=audit_log.occurred_at,
            created_at=audit_log.created_at,
        )

    async def save(self, audit_log: AuditLog) -> AuditLog:
        orm = self._to_orm(audit_log)
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._to_domain(orm)

    async def get_by_id(self, audit_id: UUID) -> AuditLog | None:
        stmt = select(AuditLogORM).where(AuditLogORM.id == audit_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: EntityType | None = None,
        action: AuditAction | None = None,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLogORM).order_by(AuditLogORM.occurred_at.desc()).offset(skip).limit(limit)
        )

        if entity_type:
            stmt = stmt.where(AuditLogORM.entity_type == entity_type)
        if action:
            stmt = stmt.where(AuditLogORM.action == action)

        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_by_entity(
        self, entity_type: EntityType, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.entity_type == entity_type, AuditLogORM.entity_id == entity_id)
            .order_by(AuditLogORM.occurred_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_by_employee(
        self, employee_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.employee_id == employee_id)
            .order_by(AuditLogORM.occurred_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_timeline(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: EntityType | None = None,
        employee_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[AuditLog]:
        stmt = (
            select(AuditLogORM).order_by(AuditLogORM.occurred_at.desc()).offset(skip).limit(limit)
        )

        if entity_type:
            stmt = stmt.where(AuditLogORM.entity_type == entity_type)
        if employee_id:
            stmt = stmt.where(AuditLogORM.employee_id == employee_id)
        if date_from:
            stmt = stmt.where(AuditLogORM.occurred_at >= date_from)
        if date_to:
            stmt = stmt.where(AuditLogORM.occurred_at <= date_to)

        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]
