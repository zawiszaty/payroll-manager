from datetime import date
from uuid import UUID

from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.repository import TimesheetRepository
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)


class CreateTimesheetService:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def create(
        self,
        employee_id: UUID,
        work_date: date,
        hours: float,
        overtime_hours: float = 0.0,
        overtime_type: OvertimeType | None = None,
        project_id: UUID | None = None,
        task_description: str | None = None,
    ) -> Timesheet:
        time_entry = TimeEntry(
            hours=hours, overtime_hours=overtime_hours, overtime_type=overtime_type
        )

        timesheet = Timesheet(
            employee_id=employee_id,
            work_date=work_date,
            time_entry=time_entry,
            project_id=project_id,
            task_description=task_description,
            status=TimesheetStatus.DRAFT,
        )

        return await self.repository.save(timesheet)


class SubmitTimesheetService:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def submit(self, timesheet_id: UUID) -> Timesheet:
        timesheet = await self.repository.get_by_id(timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {timesheet_id} not found")

        timesheet.submit()
        return await self.repository.save(timesheet)


class ApproveTimesheetService:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def approve(self, timesheet_id: UUID, approved_by: UUID) -> Timesheet:
        timesheet = await self.repository.get_by_id(timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {timesheet_id} not found")

        timesheet.approve(approved_by)
        return await self.repository.save(timesheet)


class RejectTimesheetService:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def reject(self, timesheet_id: UUID, reason: str) -> Timesheet:
        timesheet = await self.repository.get_by_id(timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {timesheet_id} not found")

        timesheet.reject(reason)
        return await self.repository.save(timesheet)


class SumHoursService:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def sum_hours_in_interval(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> float:
        return await self.repository.sum_hours_in_interval(employee_id, start_date, end_date)
