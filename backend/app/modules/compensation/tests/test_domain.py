import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.compensation.domain.models import Rate, Bonus, Deduction, Overtime, SickLeave
from app.modules.compensation.domain.value_objects import (
    RateType,
    BonusType,
    DeductionType,
    OvertimeRule,
    SickLeaveRule,
)
from app.shared.domain.value_objects import DateRange, Money


def test_rate_creation():
    rate = Rate(
        employee_id=uuid4(),
        rate_type=RateType.HOURLY_RATE,
        amount=Money(Decimal("25.00"), "USD"),
        date_range=DateRange(date(2025, 1, 1), date(2025, 12, 31)),
        description="Hourly rate for developer",
    )
    assert rate.rate_type == RateType.HOURLY_RATE
    assert rate.amount.amount == Decimal("25.00")
    assert rate.amount.currency == "USD"


def test_bonus_creation():
    bonus = Bonus(
        employee_id=uuid4(),
        bonus_type=BonusType.PERFORMANCE,
        amount=Money(Decimal("1000.00"), "USD"),
        payment_date=date(2025, 6, 30),
        description="Q2 performance bonus",
    )
    assert bonus.bonus_type == BonusType.PERFORMANCE
    assert bonus.amount.amount == Decimal("1000.00")
    assert bonus.payment_date == date(2025, 6, 30)


def test_deduction_creation():
    deduction = Deduction(
        employee_id=uuid4(),
        deduction_type=DeductionType.TAX,
        amount=Money(Decimal("500.00"), "USD"),
        date_range=DateRange(date(2025, 1, 1), None),
        description="Federal tax withholding",
    )
    assert deduction.deduction_type == DeductionType.TAX
    assert deduction.amount.amount == Decimal("500.00")
    assert deduction.date_range.valid_to is None


def test_overtime_rule_validation():
    with pytest.raises(ValueError, match="Overtime multiplier must be greater than 1.0"):
        OvertimeRule(
            multiplier=Decimal("1.0"),
            threshold_hours=40,
            date_range=DateRange(date(2025, 1, 1), None),
        )

    with pytest.raises(ValueError, match="Threshold hours must be positive"):
        OvertimeRule(
            multiplier=Decimal("1.5"),
            threshold_hours=0,
            date_range=DateRange(date(2025, 1, 1), None),
        )


def test_overtime_calculation():
    overtime = Overtime(
        employee_id=uuid4(),
        rule=OvertimeRule(
            multiplier=Decimal("1.5"),
            threshold_hours=40,
            date_range=DateRange(date(2025, 1, 1), None),
        ),
    )

    base_rate = Decimal("25.00")
    hours_worked = 45
    overtime_pay = overtime.calculate_overtime_pay(base_rate, hours_worked)

    expected_overtime_pay = base_rate * Decimal("1.5") * Decimal("5")
    assert overtime_pay == expected_overtime_pay


def test_overtime_no_overtime_hours():
    overtime = Overtime(
        employee_id=uuid4(),
        rule=OvertimeRule(
            multiplier=Decimal("1.5"),
            threshold_hours=40,
            date_range=DateRange(date(2025, 1, 1), None),
        ),
    )

    base_rate = Decimal("25.00")
    hours_worked = 35
    overtime_pay = overtime.calculate_overtime_pay(base_rate, hours_worked)

    assert overtime_pay == Decimal("0")


def test_sick_leave_rule_validation():
    with pytest.raises(ValueError, match="Sick leave percentage must be between 0 and 100"):
        SickLeaveRule(
            percentage=Decimal("110.0"),
            max_days=10,
            date_range=DateRange(date(2025, 1, 1), None),
        )

    with pytest.raises(ValueError, match="Max days must be positive if specified"):
        SickLeaveRule(
            percentage=Decimal("80.0"),
            max_days=-5,
            date_range=DateRange(date(2025, 1, 1), None),
        )


def test_sick_leave_calculation():
    sick_leave = SickLeave(
        employee_id=uuid4(),
        rule=SickLeaveRule(
            percentage=Decimal("80.0"),
            max_days=10,
            date_range=DateRange(date(2025, 1, 1), None),
        ),
    )

    monthly_salary = Decimal("6000.00")
    days_taken = 5
    sick_pay = sick_leave.calculate_sick_pay(monthly_salary, days_taken)

    expected_sick_pay = monthly_salary * (Decimal("80.0") / Decimal("100")) * Decimal("5") / Decimal("30")
    assert sick_pay == expected_sick_pay


def test_sick_leave_exceeds_max_days():
    sick_leave = SickLeave(
        employee_id=uuid4(),
        rule=SickLeaveRule(
            percentage=Decimal("80.0"),
            max_days=10,
            date_range=DateRange(date(2025, 1, 1), None),
        ),
    )

    monthly_salary = Decimal("6000.00")
    days_taken = 15
    sick_pay = sick_leave.calculate_sick_pay(monthly_salary, days_taken)

    expected_sick_pay = monthly_salary * (Decimal("80.0") / Decimal("100")) * Decimal("10") / Decimal("30")
    assert sick_pay == expected_sick_pay


def test_sick_leave_no_max_days():
    sick_leave = SickLeave(
        employee_id=uuid4(),
        rule=SickLeaveRule(
            percentage=Decimal("100.0"),
            max_days=None,
            date_range=DateRange(date(2025, 1, 1), None),
        ),
    )

    monthly_salary = Decimal("6000.00")
    days_taken = 20
    sick_pay = sick_leave.calculate_sick_pay(monthly_salary, days_taken)

    expected_sick_pay = monthly_salary * Decimal("20") / Decimal("30")
    assert sick_pay == expected_sick_pay
