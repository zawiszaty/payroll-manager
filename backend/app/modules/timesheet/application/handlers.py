from app.modules.timesheet.application.commands import (
    ApproveTimesheetCommand,
    CreateTimesheetCommand,
    DeleteTimesheetCommand,
    RejectTimesheetCommand,
    SubmitTimesheetCommand,
    UpdateTimesheetCommand,
)
from app.modules.timesheet.application.queries import (
    GetPendingApprovalQuery,
    GetTimesheetQuery,
    GetTimesheetsByEmployeeAndDateRangeQuery,
    GetTimesheetsByEmployeeQuery,
    GetTimesheetsByStatusQuery,
    ListTimesheetsQuery,
    SumHoursInIntervalQuery,
)
from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.repository import TimesheetRepository
from app.modules.timesheet.domain.services import (
    ApproveTimesheetService,
    CreateTimesheetService,
    RejectTimesheetService,
    SubmitTimesheetService,
    SumHoursService,
)
from app.modules.timesheet.domain.value_objects import OvertimeType, TimeEntry


class CreateTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository
        self.service = CreateTimesheetService(repository)

    async def handle(self, command: CreateTimesheetCommand) -> Timesheet:
        overtime_type = None
        if command.overtime_type:
            try:
                overtime_type = OvertimeType(command.overtime_type)
            except ValueError:
                raise ValueError(f"Invalid overtime type: {command.overtime_type}")

        return await self.service.create(
            employee_id=command.employee_id,
            work_date=command.work_date,
            hours=command.hours,
            overtime_hours=command.overtime_hours,
            overtime_type=overtime_type,
            project_id=command.project_id,
            task_description=command.task_description,
        )


class UpdateTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, command: UpdateTimesheetCommand) -> Timesheet:
        timesheet = await self.repository.get_by_id(command.timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {command.timesheet_id} not found")

        if not timesheet.is_draft():
            raise ValueError("Can only update timesheets in draft status")

        overtime_type = None
        if command.overtime_type:
            try:
                overtime_type = OvertimeType(command.overtime_type)
            except ValueError:
                raise ValueError(f"Invalid overtime type: {command.overtime_type}")

        timesheet.time_entry = TimeEntry(
            hours=command.hours,
            overtime_hours=command.overtime_hours,
            overtime_type=overtime_type,
        )
        timesheet.project_id = command.project_id
        timesheet.task_description = command.task_description

        return await self.repository.save(timesheet)


class SubmitTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository
        self.service = SubmitTimesheetService(repository)

    async def handle(self, command: SubmitTimesheetCommand) -> Timesheet:
        return await self.service.submit(command.timesheet_id)


class ApproveTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository
        self.service = ApproveTimesheetService(repository)

    async def handle(self, command: ApproveTimesheetCommand) -> Timesheet:
        return await self.service.approve(command.timesheet_id, command.approved_by)


class RejectTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository
        self.service = RejectTimesheetService(repository)

    async def handle(self, command: RejectTimesheetCommand) -> Timesheet:
        return await self.service.reject(command.timesheet_id, command.reason)


class DeleteTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, command: DeleteTimesheetCommand) -> None:
        timesheet = await self.repository.get_by_id(command.timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {command.timesheet_id} not found")

        if not timesheet.is_draft():
            raise ValueError("Can only delete timesheets in draft status")

        await self.repository.delete(command.timesheet_id)


class GetTimesheetHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: GetTimesheetQuery) -> Timesheet | None:
        return await self.repository.get_by_id(query.timesheet_id)


class ListTimesheetsHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: ListTimesheetsQuery) -> list[Timesheet]:
        return await self.repository.list_all()


class GetTimesheetsByEmployeeHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: GetTimesheetsByEmployeeQuery) -> list[Timesheet]:
        return await self.repository.get_by_employee(query.employee_id)


class GetTimesheetsByEmployeeAndDateRangeHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: GetTimesheetsByEmployeeAndDateRangeQuery) -> list[Timesheet]:
        return await self.repository.get_by_employee_and_date_range(
            query.employee_id, query.start_date, query.end_date
        )


class GetTimesheetsByStatusHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: GetTimesheetsByStatusQuery) -> list[Timesheet]:
        return await self.repository.get_by_status(query.status)


class GetPendingApprovalHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository

    async def handle(self, query: GetPendingApprovalQuery) -> list[Timesheet]:
        return await self.repository.get_pending_approval()


class SumHoursInIntervalHandler:
    def __init__(self, repository: TimesheetRepository):
        self.repository = repository
        self.service = SumHoursService(repository)

    async def handle(self, query: SumHoursInIntervalQuery) -> float:
        return await self.service.sum_hours_in_interval(
            query.employee_id, query.start_date, query.end_date
        )
