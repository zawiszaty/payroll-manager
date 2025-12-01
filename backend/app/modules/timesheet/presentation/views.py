from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.timesheet.domain.models import Timesheet


class CreateTimesheetRequest(BaseModel):
    employee_id: UUID
    work_date: date
    hours: float = Field(ge=0)
    overtime_hours: float = Field(default=0.0, ge=0)
    overtime_type: str | None = None
    project_id: UUID | None = None
    task_description: str | None = None


class UpdateTimesheetRequest(BaseModel):
    hours: float = Field(ge=0)
    overtime_hours: float = Field(default=0.0, ge=0)
    overtime_type: str | None = None
    project_id: UUID | None = None
    task_description: str | None = None


class ApproveTimesheetRequest(BaseModel):
    approved_by: UUID


class RejectTimesheetRequest(BaseModel):
    reason: str = Field(min_length=1)


class TimesheetResponse(BaseModel):
    id: UUID
    employee_id: UUID
    work_date: date
    hours: float
    overtime_hours: float
    overtime_type: str | None
    project_id: UUID | None
    task_description: str | None
    status: str
    rejection_reason: str | None
    total_hours: float
    created_at: date
    updated_at: date
    submitted_at: date | None
    approved_at: date | None
    approved_by: UUID | None

    @classmethod
    def from_entity(cls, timesheet: Timesheet) -> "TimesheetResponse":
        return cls(
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
            rejection_reason=timesheet.rejection_reason,
            total_hours=timesheet.total_hours,
            created_at=timesheet.created_at,
            updated_at=timesheet.updated_at,
            submitted_at=timesheet.submitted_at,
            approved_at=timesheet.approved_at,
            approved_by=timesheet.approved_by,
        )


class HoursSummaryResponse(BaseModel):
    employee_id: UUID
    start_date: date
    end_date: date
    total_hours: float
