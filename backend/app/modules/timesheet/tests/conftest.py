from datetime import date
from uuid import uuid4

import pytest

from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)


@pytest.fixture
def sample_employee_id():
    return uuid4()


@pytest.fixture
def sample_approver_id():
    return uuid4()


@pytest.fixture
def sample_project_id():
    return uuid4()


@pytest.fixture
def sample_time_entry():
    return TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)


@pytest.fixture
def sample_time_entry_with_overtime():
    return TimeEntry(hours=8.0, overtime_hours=2.0, overtime_type=OvertimeType.REGULAR)


@pytest.fixture
def sample_timesheet(sample_employee_id, sample_time_entry):
    return Timesheet(
        employee_id=sample_employee_id,
        work_date=date(2024, 1, 15),
        time_entry=sample_time_entry,
        status=TimesheetStatus.DRAFT,
    )


@pytest.fixture
def sample_timesheet_with_overtime(sample_employee_id, sample_time_entry_with_overtime):
    return Timesheet(
        employee_id=sample_employee_id,
        work_date=date(2024, 1, 16),
        time_entry=sample_time_entry_with_overtime,
        status=TimesheetStatus.DRAFT,
    )


@pytest.fixture
def submitted_timesheet(sample_employee_id, sample_time_entry):
    timesheet = Timesheet(
        employee_id=sample_employee_id,
        work_date=date(2024, 1, 17),
        time_entry=sample_time_entry,
        status=TimesheetStatus.DRAFT,
    )
    timesheet.submit()
    return timesheet
