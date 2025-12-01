from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.modules.timesheet.domain.repository import TimesheetRepository


@dataclass
class TimesheetDTO:
    id: UUID
    employee_id: UUID
    work_date: date
    hours: float
    overtime_hours: float
    overtime_type: str | None
    project_id: UUID | None
    task_description: str | None
    status: str
    total_hours: float


@dataclass
class TimesheetSummaryDTO:
    employee_id: UUID
    start_date: date
    end_date: date
    total_hours: float
    total_timesheets: int


class ITimesheetFacade(ABC):
    @abstractmethod
    async def get_timesheet(self, timesheet_id: UUID) -> TimesheetDTO | None:
        pass

    @abstractmethod
    async def get_timesheets_by_employee(self, employee_id: UUID) -> list[TimesheetDTO]:
        pass

    @abstractmethod
    async def get_approved_timesheets_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[TimesheetDTO]:
        pass

    @abstractmethod
    async def sum_hours_in_interval(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> float:
        pass

    @abstractmethod
    async def get_timesheet_summary(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> TimesheetSummaryDTO:
        pass


class TimesheetFacade(ITimesheetFacade):
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def get_timesheet(self, timesheet_id: UUID) -> TimesheetDTO | None:
        timesheet = await self.repository.get_by_id(timesheet_id)
        if not timesheet:
            return None

        return TimesheetDTO(
            id=timesheet.id,
            employee_id=timesheet.employee_id,
            work_date=timesheet.work_date,
            hours=timesheet.regular_hours,
            overtime_hours=timesheet.overtime_hours,
            overtime_type=timesheet.time_entry.overtime_type.value
            if timesheet.time_entry.overtime_type
            else None,
            project_id=timesheet.project_id,
            task_description=timesheet.task_description,
            status=timesheet.status.value,
            total_hours=timesheet.total_hours,
        )

    async def get_timesheets_by_employee(self, employee_id: UUID) -> list[TimesheetDTO]:
        timesheets = await self.repository.get_by_employee(employee_id)
        return [
            TimesheetDTO(
                id=ts.id,
                employee_id=ts.employee_id,
                work_date=ts.work_date,
                hours=ts.regular_hours,
                overtime_hours=ts.overtime_hours,
                overtime_type=ts.time_entry.overtime_type.value
                if ts.time_entry.overtime_type
                else None,
                project_id=ts.project_id,
                task_description=ts.task_description,
                status=ts.status.value,
                total_hours=ts.total_hours,
            )
            for ts in timesheets
        ]

    async def get_approved_timesheets_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> list[TimesheetDTO]:
        timesheets = await self.repository.get_by_employee_and_date_range(
            employee_id, start_date, end_date
        )
        approved_timesheets = [ts for ts in timesheets if ts.is_approved()]

        return [
            TimesheetDTO(
                id=ts.id,
                employee_id=ts.employee_id,
                work_date=ts.work_date,
                hours=ts.regular_hours,
                overtime_hours=ts.overtime_hours,
                overtime_type=ts.time_entry.overtime_type.value
                if ts.time_entry.overtime_type
                else None,
                project_id=ts.project_id,
                task_description=ts.task_description,
                status=ts.status.value,
                total_hours=ts.total_hours,
            )
            for ts in approved_timesheets
        ]

    async def sum_hours_in_interval(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> float:
        return await self.repository.sum_hours_in_interval(employee_id, start_date, end_date)

    async def get_timesheet_summary(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> TimesheetSummaryDTO:
        total_hours = await self.sum_hours_in_interval(employee_id, start_date, end_date)
        timesheets = await self.repository.get_by_employee_and_date_range(
            employee_id, start_date, end_date
        )
        approved_count = len([ts for ts in timesheets if ts.is_approved()])

        return TimesheetSummaryDTO(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            total_hours=total_hours,
            total_timesheets=approved_count,
        )
