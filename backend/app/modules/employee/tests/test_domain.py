from datetime import date

import pytest

from app.modules.employee.domain.models import Employee
from app.modules.employee.domain.value_objects import EmploymentStatus, EmploymentStatusType
from app.shared.domain.value_objects import DateRange


def test_employee_creation():
    employee = Employee(first_name="John", last_name="Doe", email="john@example.com")
    assert employee.first_name == "John"
    assert employee.last_name == "Doe"
    assert employee.full_name == "John Doe"


def test_add_status():
    employee = Employee(first_name="John", last_name="Doe", email="john@example.com")

    status = EmploymentStatus(
        status_type=EmploymentStatusType.ACTIVE, date_range=DateRange(valid_from=date(2024, 1, 1))
    )

    employee.add_status(status)
    assert len(employee.statuses) == 1
    assert employee.statuses[0].status_type == EmploymentStatusType.ACTIVE


def test_overlapping_status_raises_error():
    employee = Employee(first_name="John", last_name="Doe", email="john@example.com")

    status1 = EmploymentStatus(
        status_type=EmploymentStatusType.ACTIVE, date_range=DateRange(valid_from=date(2024, 1, 1))
    )
    employee.add_status(status1)

    status2 = EmploymentStatus(
        status_type=EmploymentStatusType.ON_LEAVE, date_range=DateRange(valid_from=date(2024, 6, 1))
    )

    with pytest.raises(ValueError, match="Status periods cannot overlap"):
        employee.add_status(status2)


def test_get_status_at():
    employee = Employee(first_name="John", last_name="Doe", email="john@example.com")

    status = EmploymentStatus(
        status_type=EmploymentStatusType.ACTIVE,
        date_range=DateRange(valid_from=date(2024, 1, 1), valid_to=date(2024, 12, 31)),
    )
    employee.add_status(status)

    assert employee.get_status_at(date(2024, 6, 1)) is not None
    assert employee.get_status_at(date(2023, 12, 31)) is None
    assert employee.get_status_at(date(2025, 1, 1)) is None


def test_is_active_at():
    employee = Employee(first_name="John", last_name="Doe", email="john@example.com")

    status = EmploymentStatus(
        status_type=EmploymentStatusType.ACTIVE, date_range=DateRange(valid_from=date(2024, 1, 1))
    )
    employee.add_status(status)

    assert employee.is_active_at(date(2024, 6, 1)) is True
