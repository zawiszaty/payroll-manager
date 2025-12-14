from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class CreateTimesheetCommand:
    employee_id: UUID
    start_date: date
    end_date: date
    hours: float
    overtime_hours: float = 0.0
    overtime_type: str | None = None
    project_id: UUID | None = None
    task_description: str | None = None


@dataclass
class UpdateTimesheetCommand:
    timesheet_id: UUID
    hours: float
    overtime_hours: float = 0.0
    overtime_type: str | None = None
    project_id: UUID | None = None
    task_description: str | None = None


@dataclass
class SubmitTimesheetCommand:
    timesheet_id: UUID


@dataclass
class ApproveTimesheetCommand:
    timesheet_id: UUID
    approved_by: UUID


@dataclass
class RejectTimesheetCommand:
    timesheet_id: UUID
    reason: str


@dataclass
class DeleteTimesheetCommand:
    timesheet_id: UUID
