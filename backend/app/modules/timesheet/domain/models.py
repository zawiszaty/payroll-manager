from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from app.modules.timesheet.domain.value_objects import (
    TimeEntry,
    TimesheetStatus,
)


@dataclass
class Timesheet:
    employee_id: UUID
    start_date: date
    end_date: date
    time_entry: TimeEntry
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

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("End date must be after or equal to start date")

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
