from datetime import date
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.timesheet.api.facade import TimesheetFacade
from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)
from app.modules.timesheet.infrastructure.repository import (
    SQLAlchemyTimesheetRepository,
)


@pytest.mark.asyncio
async def test_get_timesheet(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    employee_id = uuid4()
    time_entry = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    timesheet = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 15),
        time_entry=time_entry,
        status=TimesheetStatus.DRAFT,
    )
    saved = await repository.save(timesheet)
    await test_session.commit()

    dto = await facade.get_timesheet(saved.id)

    assert dto is not None
    assert dto.id == saved.id
    assert dto.employee_id == employee_id
    assert dto.hours == 8.0
    assert dto.total_hours == 8.0


@pytest.mark.asyncio
async def test_get_timesheet_not_found(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    dto = await facade.get_timesheet(uuid4())

    assert dto is None


@pytest.mark.asyncio
async def test_get_timesheets_by_employee(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    employee_id = uuid4()

    time_entry1 = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    timesheet1 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 15),
        time_entry=time_entry1,
        status=TimesheetStatus.DRAFT,
    )
    await repository.save(timesheet1)

    time_entry2 = TimeEntry(hours=7.5, overtime_hours=0.0, overtime_type=None)
    timesheet2 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 16),
        time_entry=time_entry2,
        status=TimesheetStatus.DRAFT,
    )
    await repository.save(timesheet2)
    await test_session.commit()

    dtos = await facade.get_timesheets_by_employee(employee_id)

    assert len(dtos) == 2
    assert all(dto.employee_id == employee_id for dto in dtos)


@pytest.mark.asyncio
async def test_get_approved_timesheets_in_period(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    employee_id = uuid4()
    approver_id = uuid4()

    time_entry = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    timesheet1 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 15),
        time_entry=time_entry,
        status=TimesheetStatus.DRAFT,
    )
    timesheet1.submit()
    timesheet1.approve(approver_id)
    await repository.save(timesheet1)

    timesheet2 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 16),
        time_entry=time_entry,
        status=TimesheetStatus.DRAFT,
    )
    await repository.save(timesheet2)
    await test_session.commit()

    dtos = await facade.get_approved_timesheets_in_period(
        employee_id, date(2024, 1, 15), date(2024, 1, 16)
    )

    assert len(dtos) == 1
    assert dtos[0].status == "approved"


@pytest.mark.asyncio
async def test_sum_hours_in_interval(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    employee_id = uuid4()
    approver_id = uuid4()

    time_entry1 = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    timesheet1 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 15),
        time_entry=time_entry1,
        status=TimesheetStatus.DRAFT,
    )
    timesheet1.submit()
    timesheet1.approve(approver_id)
    await repository.save(timesheet1)

    time_entry2 = TimeEntry(hours=7.5, overtime_hours=1.5, overtime_type=OvertimeType.REGULAR)
    timesheet2 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 16),
        time_entry=time_entry2,
        status=TimesheetStatus.DRAFT,
    )
    timesheet2.submit()
    timesheet2.approve(approver_id)
    await repository.save(timesheet2)
    await test_session.commit()

    total = await facade.sum_hours_in_interval(employee_id, date(2024, 1, 15), date(2024, 1, 16))

    assert total == 17.0


@pytest.mark.asyncio
async def test_get_timesheet_summary(test_session: AsyncSession):
    repository = SQLAlchemyTimesheetRepository(test_session)
    facade = TimesheetFacade(repository)

    employee_id = uuid4()
    approver_id = uuid4()

    time_entry1 = TimeEntry(hours=8.0, overtime_hours=0.0, overtime_type=None)
    timesheet1 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 15),
        time_entry=time_entry1,
        status=TimesheetStatus.DRAFT,
    )
    timesheet1.submit()
    timesheet1.approve(approver_id)
    await repository.save(timesheet1)

    time_entry2 = TimeEntry(hours=7.5, overtime_hours=0.0, overtime_type=None)
    timesheet2 = Timesheet(
        employee_id=employee_id,
        initial_work_date=date(2024, 1, 16),
        time_entry=time_entry2,
        status=TimesheetStatus.DRAFT,
    )
    timesheet2.submit()
    timesheet2.approve(approver_id)
    await repository.save(timesheet2)
    await test_session.commit()

    summary = await facade.get_timesheet_summary(employee_id, date(2024, 1, 15), date(2024, 1, 16))

    assert summary.employee_id == employee_id
    assert summary.total_hours == 15.5
    assert summary.total_timesheets == 2
