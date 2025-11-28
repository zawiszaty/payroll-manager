from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.absence.domain.entities import Absence, AbsenceBalance
from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType
from app.shared.domain.value_objects import DateRange


def test_absence_creation():
    employee_id = uuid4()
    absence = Absence(
        employee_id=employee_id,
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
        reason="Summer vacation",
    )

    assert absence.employee_id == employee_id
    assert absence.absence_type == AbsenceType.VACATION
    assert absence.status == AbsenceStatus.PENDING
    assert absence.reason == "Summer vacation"


def test_absence_calculate_days():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )

    assert absence.calculate_days() == Decimal("10")


def test_absence_approve():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )

    absence.approve()
    assert absence.status == AbsenceStatus.APPROVED


def test_absence_reject():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )

    absence.reject()
    assert absence.status == AbsenceStatus.REJECTED


def test_absence_cancel():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )

    absence.cancel()
    assert absence.status == AbsenceStatus.CANCELLED


def test_cannot_approve_non_pending_absence():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )
    absence.approve()

    with pytest.raises(ValueError, match="Cannot approve absence with status"):
        absence.approve()


def test_absence_is_active_at():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )
    absence.approve()

    assert absence.is_active_at(date(2025, 6, 5)) is True
    assert absence.is_active_at(date(2025, 5, 31)) is False
    assert absence.is_active_at(date(2025, 6, 11)) is False


def test_absence_overlaps_with():
    absence = Absence(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        period=DateRange(date(2025, 6, 1), date(2025, 6, 10)),
    )

    overlapping_period = DateRange(date(2025, 6, 5), date(2025, 6, 15))
    non_overlapping_period = DateRange(date(2025, 6, 11), date(2025, 6, 20))

    assert absence.overlaps_with(overlapping_period) is True
    assert absence.overlaps_with(non_overlapping_period) is False


def test_absence_balance_creation():
    employee_id = uuid4()
    balance = AbsenceBalance(
        employee_id=employee_id,
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
    )

    assert balance.employee_id == employee_id
    assert balance.absence_type == AbsenceType.VACATION
    assert balance.year == 2025
    assert balance.total_days == Decimal("20")
    assert balance.used_days == Decimal("0")


def test_absence_balance_remaining_days():
    balance = AbsenceBalance(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
        used_days=Decimal("5"),
    )

    assert balance.remaining_days() == Decimal("15")


def test_absence_balance_can_take_absence():
    balance = AbsenceBalance(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
        used_days=Decimal("15"),
    )

    assert balance.can_take_absence(Decimal("5")) is True
    assert balance.can_take_absence(Decimal("6")) is False


def test_absence_balance_use_days():
    balance = AbsenceBalance(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
    )

    balance.use_days(Decimal("5"))
    assert balance.used_days == Decimal("5")
    assert balance.remaining_days() == Decimal("15")


def test_absence_balance_use_days_insufficient():
    balance = AbsenceBalance(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
        used_days=Decimal("18"),
    )

    with pytest.raises(ValueError, match="Insufficient balance"):
        balance.use_days(Decimal("5"))


def test_absence_balance_return_days():
    balance = AbsenceBalance(
        employee_id=uuid4(),
        absence_type=AbsenceType.VACATION,
        year=2025,
        total_days=Decimal("20"),
        used_days=Decimal("10"),
    )

    balance.return_days(Decimal("5"))
    assert balance.used_days == Decimal("5")
    assert balance.remaining_days() == Decimal("15")


def test_absence_balance_validation():
    with pytest.raises(ValueError, match="Total days cannot be negative"):
        AbsenceBalance(
            employee_id=uuid4(),
            absence_type=AbsenceType.VACATION,
            year=2025,
            total_days=Decimal("-10"),
        )

    with pytest.raises(ValueError, match="Year must be between 2000 and 2100"):
        AbsenceBalance(
            employee_id=uuid4(),
            absence_type=AbsenceType.VACATION,
            year=1999,
            total_days=Decimal("20"),
        )
