import pytest
from datetime import date
from uuid import uuid4

from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)


def test_create_time_entry_without_overtime():
    time_entry = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    assert time_entry.hours == 8.0
    assert time_entry.overtime_hours == 0.0
    assert time_entry.overtime_type is None
    assert time_entry.total_hours == 8.0


def test_create_time_entry_with_overtime():
    time_entry = TimeEntry(
        hours=8.0, overtime_hours=2.0, overtime_type=OvertimeType.REGULAR
    )
    assert time_entry.hours == 8.0
    assert time_entry.overtime_hours == 2.0
    assert time_entry.overtime_type == OvertimeType.REGULAR
    assert time_entry.total_hours == 10.0


def test_time_entry_requires_overtime_type_when_overtime_hours():
    with pytest.raises(ValueError, match="Overtime type required"):
        TimeEntry(hours=8.0, overtime_hours=2.0, overtime_type=None)


def test_time_entry_rejects_overtime_type_when_no_overtime_hours():
    with pytest.raises(ValueError, match="Overtime type should be None"):
        TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=OvertimeType.REGULAR)


def test_time_entry_rejects_negative_hours():
    with pytest.raises(ValueError, match="Hours cannot be negative"):
        TimeEntry(hours=-1.0, overtime_hours=0.0, overtime_type=None)


def test_time_entry_rejects_negative_overtime_hours():
    with pytest.raises(ValueError, match="Overtime hours cannot be negative"):
        TimeEntry(hours=8.0, overtime_hours=-1.0, overtime_type=None)


def test_create_timesheet(sample_employee_id, sample_time_entry):
    timesheet = Timesheet(
        employee_id=sample_employee_id,
        work_date=date(2024, 1, 15),
        time_entry=sample_time_entry,
        status=TimesheetStatus.DRAFT,
    )

    assert timesheet.employee_id == sample_employee_id
    assert timesheet.work_date == date(2024, 1, 15)
    assert timesheet.time_entry == sample_time_entry
    assert timesheet.status == TimesheetStatus.DRAFT
    assert timesheet.is_draft()
    assert not timesheet.is_submitted()
    assert not timesheet.is_approved()
    assert not timesheet.is_rejected()


def test_timesheet_submit(sample_timesheet):
    sample_timesheet.submit()

    assert sample_timesheet.status == TimesheetStatus.SUBMITTED
    assert sample_timesheet.submitted_at is not None
    assert sample_timesheet.is_submitted()


def test_timesheet_cannot_submit_twice(sample_timesheet):
    sample_timesheet.submit()

    with pytest.raises(ValueError, match="Cannot submit timesheet"):
        sample_timesheet.submit()


def test_timesheet_approve(submitted_timesheet, sample_approver_id):
    submitted_timesheet.approve(sample_approver_id)

    assert submitted_timesheet.status == TimesheetStatus.APPROVED
    assert submitted_timesheet.approved_at is not None
    assert submitted_timesheet.approved_by == sample_approver_id
    assert submitted_timesheet.rejection_reason is None
    assert submitted_timesheet.is_approved()


def test_timesheet_cannot_approve_draft(sample_timesheet, sample_approver_id):
    with pytest.raises(ValueError, match="Cannot approve timesheet"):
        sample_timesheet.approve(sample_approver_id)


def test_timesheet_reject(submitted_timesheet):
    submitted_timesheet.reject("Hours not matching project requirements")

    assert submitted_timesheet.status == TimesheetStatus.REJECTED
    assert submitted_timesheet.rejection_reason == "Hours not matching project requirements"
    assert submitted_timesheet.is_rejected()


def test_timesheet_cannot_reject_draft(sample_timesheet):
    with pytest.raises(ValueError, match="Cannot reject timesheet"):
        sample_timesheet.reject("Some reason")


def test_timesheet_reject_requires_reason(submitted_timesheet):
    with pytest.raises(ValueError, match="Rejection reason is required"):
        submitted_timesheet.reject("")


def test_timesheet_total_hours(sample_timesheet_with_overtime):
    assert sample_timesheet_with_overtime.total_hours == 10.0
    assert sample_timesheet_with_overtime.regular_hours == 8.0
    assert sample_timesheet_with_overtime.overtime_hours == 2.0


def test_timesheet_with_project_and_task(sample_employee_id, sample_time_entry, sample_project_id):
    timesheet = Timesheet(
        employee_id=sample_employee_id,
        work_date=date(2024, 1, 15),
        time_entry=sample_time_entry,
        project_id=sample_project_id,
        task_description="Implemented user authentication",
        status=TimesheetStatus.DRAFT,
    )

    assert timesheet.project_id == sample_project_id
    assert timesheet.task_description == "Implemented user authentication"
