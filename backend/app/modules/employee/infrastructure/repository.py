import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.employee.domain.models import Employee
from app.modules.employee.domain.repository import EmployeeRepository
from app.modules.employee.domain.value_objects import EmploymentStatus
from app.modules.employee.infrastructure.models import EmployeeORM, EmploymentStatusORM
from app.shared.domain.events import get_event_dispatcher
from app.shared.domain.value_objects import DateRange

logger = logging.getLogger(__name__)


class SQLAlchemyEmployeeRepository(EmployeeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.event_dispatcher = get_event_dispatcher()

    async def _dispatch_events(self, employee: Employee) -> None:
        """
        Dispatch all domain events for the employee.
        Errors are logged but don't prevent the operation from succeeding.
        """
        events = employee.get_domain_events()
        if not events:
            return

        try:
            # Dispatch all events sequentially to ensure they propagate
            for event in events:
                try:
                    await self.event_dispatcher.dispatch(event)
                    logger.debug(f"Successfully dispatched event: {event.__class__.__name__}")
                except Exception as e:
                    # Log the error with context but don't fail the entire operation
                    logger.error(
                        f"Failed to dispatch event {event.__class__.__name__} "
                        f"for employee {employee.id}: {e}",
                        exc_info=True,
                    )
                    # In production, you might want to queue failed events for retry
        finally:
            # Always clear events even if dispatch fails to avoid re-dispatch
            employee.clear_domain_events()

    def _to_domain(self, orm: EmployeeORM) -> Employee:
        statuses = [
            EmploymentStatus(
                status_type=s.status_type,
                date_range=DateRange(valid_from=s.valid_from, valid_to=s.valid_to),
                reason=s.reason,
            )
            for s in orm.statuses
        ]

        return Employee(
            id=orm.id,
            first_name=orm.first_name,
            last_name=orm.last_name,
            email=orm.email,
            phone=orm.phone,
            date_of_birth=orm.date_of_birth,
            hire_date=orm.hire_date,
            statuses=statuses,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    def _to_orm(self, employee: Employee) -> EmployeeORM:
        orm = EmployeeORM(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            phone=employee.phone,
            date_of_birth=employee.date_of_birth,
            hire_date=employee.hire_date,
        )

        orm.statuses = [
            EmploymentStatusORM(
                status_type=s.status_type,
                valid_from=s.date_range.valid_from,
                valid_to=s.date_range.valid_to,
                reason=s.reason,
            )
            for s in employee.statuses
        ]

        return orm

    async def save(self, employee: Employee) -> Employee:
        """Save an employee to the database (add or update)."""
        orm = self._to_orm(employee)
        merged_orm = await self.session.merge(orm)
        await self.session.flush()
        await self.session.refresh(merged_orm)
        # Load statuses relationship
        await self.session.refresh(merged_orm, ["statuses"])
        return self._to_domain(merged_orm)

    async def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        stmt = (
            select(EmployeeORM)
            .options(selectinload(EmployeeORM.statuses))
            .where(EmployeeORM.id == employee_id)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_email(self, email: str) -> Optional[Employee]:
        stmt = (
            select(EmployeeORM)
            .options(selectinload(EmployeeORM.statuses))
            .where(EmployeeORM.email == email)
        )
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list(self, page: int = 1, limit: int = 100) -> List[Employee]:
        skip = (page - 1) * limit
        stmt = (
            select(EmployeeORM)
            .options(selectinload(EmployeeORM.statuses))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def delete(self, employee_id: UUID) -> bool:
        stmt = select(EmployeeORM).where(EmployeeORM.id == employee_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return False

        await self.session.delete(orm)
        return True
