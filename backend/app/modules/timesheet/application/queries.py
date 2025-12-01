from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class GetTimesheetQuery:
    timesheet_id: UUID


@dataclass
class ListTimesheetsQuery:
    pass


@dataclass
class GetTimesheetsByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetTimesheetsByEmployeeAndDateRangeQuery:
    employee_id: UUID
    start_date: date
    end_date: date


@dataclass
class GetTimesheetsByStatusQuery:
    status: str


@dataclass
class GetPendingApprovalQuery:
    pass


@dataclass
class SumHoursInIntervalQuery:
    employee_id: UUID
    start_date: date
    end_date: date
