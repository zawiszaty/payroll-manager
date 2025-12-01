from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.modules.timesheet.domain.models import Timesheet
from app.modules.timesheet.domain.value_objects import (
    OvertimeType,
    TimeEntry,
    TimesheetStatus,
)


@pytest_asyncio.fixture
async def test_engine():
    test_database_url = (
        "postgresql+asyncpg://payroll_user:payroll_pass@postgres:5432/payroll_db_test"
    )
    engine = create_async_engine(test_database_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


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
