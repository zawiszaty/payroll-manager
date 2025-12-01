from datetime import date
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.repository import TimesheetRepository
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)
from app.modules.timesheet.infrastructure.models import TimesheetORM


class SQLAlchemyTimesheetRepository(TimesheetRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, orm: TimesheetORM) -> Timesheet:
        time_entry = TimeEntry(
            hours=orm.hours,
            overtime_hours=orm.overtime_hours,
            overtime_type=OvertimeType(orm.overtime_type)
            if orm.overtime_type
            else None,
        )

        return Timesheet(
            id=orm.id,
            employee_id=orm.employee_id,
            work_date=orm.work_date,
            time_entry=time_entry,
            project_id=orm.project_id,
            task_description=orm.task_description,
            status=TimesheetStatus(orm.status),
            rejection_reason=orm.rejection_reason,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            submitted_at=orm.submitted_at,
            approved_at=orm.approved_at,
            approved_by=orm.approved_by,
        )

    def _to_orm(self, domain: Timesheet) -> TimesheetORM:
        return TimesheetORM(
            id=domain.id,
            employee_id=domain.employee_id,
            work_date=domain.work_date,
            hours=domain.time_entry.hours,
            overtime_hours=domain.time_entry.overtime_hours,
            overtime_type=domain.time_entry.overtime_type.value
            if domain.time_entry.overtime_type
            else None,
            project_id=domain.project_id,
            task_description=domain.task_description,
            status=domain.status.value,
            rejection_reason=domain.rejection_reason,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            submitted_at=domain.submitted_at,
            approved_at=domain.approved_at,
            approved_by=domain.approved_by,
        )

    async def save(self, timesheet: Timesheet) -> Timesheet:
        result = await self.session.execute(
            select(TimesheetORM).where(TimesheetORM.id == timesheet.id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.employee_id = timesheet.employee_id
            existing.work_date = timesheet.work_date
            existing.hours = timesheet.time_entry.hours
            existing.overtime_hours = timesheet.time_entry.overtime_hours
            existing.overtime_type = (
                timesheet.time_entry.overtime_type.value
                if timesheet.time_entry.overtime_type
                else None
            )
            existing.project_id = timesheet.project_id
            existing.task_description = timesheet.task_description
            existing.status = timesheet.status.value
            existing.rejection_reason = timesheet.rejection_reason
            existing.updated_at = timesheet.updated_at
            existing.submitted_at = timesheet.submitted_at
            existing.approved_at = timesheet.approved_at
            existing.approved_by = timesheet.approved_by
            await self.session.flush()
            await self.session.refresh(existing)
            return self._to_domain(existing)
        else:
            orm = self._to_orm(timesheet)
            self.session.add(orm)
            await self.session.flush()
            await self.session.refresh(orm)
            return self._to_domain(orm)

    async def get_by_id(self, timesheet_id: UUID) -> Timesheet | None:
        result = await self.session.execute(
            select(TimesheetORM).where(TimesheetORM.id == timesheet_id)
        )
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> list[Timesheet]:
        result = await self.session.execute(
            select(TimesheetORM).order_by(TimesheetORM.work_date.desc())
        )
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_by_employee(self, employee_id: UUID) -> list[Timesheet]:
        result = await self.session.execute(
            select(TimesheetORM)
            .where(TimesheetORM.employee_id == employee_id)
            .order_by(TimesheetORM.work_date.desc())
        )
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_by_employee_and_date_range(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[Timesheet]:
        result = await self.session.execute(
            select(TimesheetORM)
            .where(
                TimesheetORM.employee_id == employee_id,
                TimesheetORM.work_date >= start_date,
                TimesheetORM.work_date <= end_date,
            )
            .order_by(TimesheetORM.work_date.asc())
        )
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_by_status(self, status: str) -> list[Timesheet]:
        result = await self.session.execute(
            select(TimesheetORM)
            .where(TimesheetORM.status == status)
            .order_by(TimesheetORM.work_date.desc())
        )
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms]

    async def get_pending_approval(self) -> list[Timesheet]:
        return await self.get_by_status(TimesheetStatus.SUBMITTED.value)

    async def sum_hours_in_interval(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> float:
        result = await self.session.execute(
            select(
                func.sum(TimesheetORM.hours + TimesheetORM.overtime_hours).label(
                    "total_hours"
                )
            ).where(
                TimesheetORM.employee_id == employee_id,
                TimesheetORM.work_date >= start_date,
                TimesheetORM.work_date <= end_date,
                TimesheetORM.status == TimesheetStatus.APPROVED.value,
            )
        )
        total = result.scalar_one_or_none()
        return float(total) if total else 0.0

    async def delete(self, timesheet_id: UUID) -> None:
        result = await self.session.execute(
            select(TimesheetORM).where(TimesheetORM.id == timesheet_id)
        )
        orm = result.scalar_one_or_none()
        if orm:
            await self.session.delete(orm)
            await self.session.flush()
