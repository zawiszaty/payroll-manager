from dataclasses import InitVar, dataclass, field
from datetime import date
from uuid import UUID, uuid4

from app.modules.timesheet.domain.value_objects import (
    TimeEntry,
    TimesheetStatus,
)


@dataclass
class Timesheet:
    employee_id: UUID
    time_entry: TimeEntry
    start_date: date | None = None
    end_date: date | None = None
    project_id: UUID | None = None
    task_description: str | None = None
    status: TimesheetStatus = TimesheetStatus.DRAFT
    rejection_reason: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)
    submitted_at: date | None = None
    approved_at: date | None = None
    approved_by: UUID | None = None
    initial_work_date: InitVar[date | None] = None

    def __post_init__(self, initial_work_date: date | None) -> None:
        resolved_start = initial_work_date or self.start_date
        resolved_end = initial_work_date or self.end_date

        if resolved_start is None or resolved_end is None:
            raise ValueError("Timesheet requires a start_date/end_date or work_date")

        if resolved_end < resolved_start:
            raise ValueError("End date must be after or equal to start date")

        object.__setattr__(self, "start_date", resolved_start)
        object.__setattr__(self, "end_date", resolved_end)

    def submit(self) -> None:
        if self.status != TimesheetStatus.DRAFT:
            raise ValueError(f"Cannot submit timesheet with status {self.status.value}")
        self.status = TimesheetStatus.SUBMITTED
        self.submitted_at = date.today()
        self.updated_at = date.today()

    def approve(self, approved_by: UUID) -> None:
        if self.status != TimesheetStatus.SUBMITTED:
            raise ValueError(f"Cannot approve timesheet with status {self.status.value}")
        self.status = TimesheetStatus.APPROVED
        self.approved_at = date.today()
        self.approved_by = approved_by
        self.rejection_reason = None
        self.updated_at = date.today()

    def reject(self, reason: str) -> None:
        if self.status != TimesheetStatus.SUBMITTED:
            raise ValueError(f"Cannot reject timesheet with status {self.status.value}")
        if not reason or not reason.strip():
            raise ValueError("Rejection reason is required")
        self.status = TimesheetStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = date.today()

    def is_approved(self) -> bool:
        return self.status == TimesheetStatus.APPROVED

    def is_submitted(self) -> bool:
        return self.status == TimesheetStatus.SUBMITTED

    def is_draft(self) -> bool:
        return self.status == TimesheetStatus.DRAFT

    def is_rejected(self) -> bool:
        return self.status == TimesheetStatus.REJECTED

    @property
    def total_hours(self) -> float:
        return self.time_entry.total_hours

    @property
    def regular_hours(self) -> float:
        return self.time_entry.hours

    @property
    def overtime_hours(self) -> float:
        return self.time_entry.overtime_hours

    @property
    def work_date(self) -> date:
        if self.start_date is None:
            raise ValueError("Timesheet start_date is not set")
        return self.start_date
