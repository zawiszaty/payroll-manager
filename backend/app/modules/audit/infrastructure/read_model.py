from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.domain.value_objects import AuditAction, EntityType
from app.modules.audit.infrastructure.models import AuditLogORM
from app.modules.audit.presentation.views import AuditLogResponse


class AuditLogReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, audit_log_id: UUID) -> Optional[AuditLogResponse]:
        stmt = select(AuditLogORM).where(AuditLogORM.id == audit_log_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return AuditLogResponse(
            id=orm.id,
            entity_type=orm.entity_type.value,
            entity_id=orm.entity_id,
            employee_id=orm.employee_id,
            action=orm.action.value,
            old_values=orm.old_values,
            new_values=orm.new_values,
            changed_by=orm.changed_by,
            metadata=orm.event_metadata,
            occurred_at=orm.occurred_at,
            created_at=orm.created_at,
        )

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[EntityType] = None,
        action: Optional[AuditAction] = None,
    ) -> tuple[list[AuditLogResponse], int]:
        count_stmt = select(func.count()).select_from(AuditLogORM)
        if entity_type:
            count_stmt = count_stmt.where(AuditLogORM.entity_type == entity_type)
        if action:
            count_stmt = count_stmt.where(AuditLogORM.action == action)

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(AuditLogORM).offset(skip).limit(limit).order_by(AuditLogORM.occurred_at.desc())
        )

        if entity_type:
            stmt = stmt.where(AuditLogORM.entity_type == entity_type)
        if action:
            stmt = stmt.where(AuditLogORM.action == action)

        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AuditLogResponse(
                id=orm.id,
                entity_type=orm.entity_type.value,
                entity_id=orm.entity_id,
                employee_id=orm.employee_id,
                action=orm.action.value,
                old_values=orm.old_values,
                new_values=orm.new_values,
                changed_by=orm.changed_by,
                metadata=orm.event_metadata,
                occurred_at=orm.occurred_at,
                created_at=orm.created_at,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_entity(
        self, entity_type: EntityType, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[AuditLogResponse], int]:
        count_stmt = (
            select(func.count())
            .select_from(AuditLogORM)
            .where(AuditLogORM.entity_type == entity_type)
            .where(AuditLogORM.entity_id == entity_id)
        )
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.entity_type == entity_type)
            .where(AuditLogORM.entity_id == entity_id)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogORM.occurred_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AuditLogResponse(
                id=orm.id,
                entity_type=orm.entity_type.value,
                entity_id=orm.entity_id,
                employee_id=orm.employee_id,
                action=orm.action.value,
                old_values=orm.old_values,
                new_values=orm.new_values,
                changed_by=orm.changed_by,
                metadata=orm.event_metadata,
                occurred_at=orm.occurred_at,
                created_at=orm.created_at,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(
        self, employee_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[AuditLogResponse], int]:
        count_stmt = (
            select(func.count())
            .select_from(AuditLogORM)
            .where(AuditLogORM.employee_id == employee_id)
        )
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(AuditLogORM)
            .where(AuditLogORM.employee_id == employee_id)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogORM.occurred_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AuditLogResponse(
                id=orm.id,
                entity_type=orm.entity_type.value,
                entity_id=orm.entity_id,
                employee_id=orm.employee_id,
                action=orm.action.value,
                old_values=orm.old_values,
                new_values=orm.new_values,
                changed_by=orm.changed_by,
                metadata=orm.event_metadata,
                occurred_at=orm.occurred_at,
                created_at=orm.created_at,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_timeline(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_type: Optional[EntityType] = None,
        employee_id: Optional[UUID] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> tuple[list[AuditLogResponse], int]:
        count_stmt = select(func.count()).select_from(AuditLogORM)
        stmt = select(AuditLogORM)

        if entity_type:
            count_stmt = count_stmt.where(AuditLogORM.entity_type == entity_type)
            stmt = stmt.where(AuditLogORM.entity_type == entity_type)

        if employee_id:
            count_stmt = count_stmt.where(AuditLogORM.employee_id == employee_id)
            stmt = stmt.where(AuditLogORM.employee_id == employee_id)

        if date_from:
            count_stmt = count_stmt.where(AuditLogORM.occurred_at >= date_from)
            stmt = stmt.where(AuditLogORM.occurred_at >= date_from)

        if date_to:
            count_stmt = count_stmt.where(AuditLogORM.occurred_at <= date_to)
            stmt = stmt.where(AuditLogORM.occurred_at <= date_to)

        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = stmt.offset(skip).limit(limit).order_by(AuditLogORM.occurred_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AuditLogResponse(
                id=orm.id,
                entity_type=orm.entity_type.value,
                entity_id=orm.entity_id,
                employee_id=orm.employee_id,
                action=orm.action.value,
                old_values=orm.old_values,
                new_values=orm.new_values,
                changed_by=orm.changed_by,
                metadata=orm.event_metadata,
                occurred_at=orm.occurred_at,
                created_at=orm.created_at,
            )
            for orm in orms
        ]

        return items, total_count
