from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from app.modules.compensation.domain.value_objects import (
    BonusType,
    DeductionType,
    OvertimeRule,
    RateType,
    SickLeaveRule,
)
from app.shared.domain.value_objects import DateRange, Money


@dataclass
class Rate:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    rate_type: RateType = RateType.BASE_SALARY
    amount: Money = None
    date_range: DateRange = None
    description: Optional[str] = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def is_active_at(self, check_date: date) -> bool:
        return self.date_range.is_active_at(check_date)


@dataclass
class Bonus:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    bonus_type: BonusType = BonusType.PERFORMANCE
    amount: Money = None
    payment_date: date = field(default_factory=date.today)
    description: Optional[str] = None
    created_at: date = field(default_factory=date.today)


@dataclass
class Deduction:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    deduction_type: DeductionType = DeductionType.TAX
    amount: Money = None
    date_range: DateRange = None
    description: Optional[str] = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def is_active_at(self, check_date: date) -> bool:
        return self.date_range.is_active_at(check_date)


@dataclass
class Overtime:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    rule: OvertimeRule = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def calculate_overtime_pay(self, base_rate: Decimal, hours: int) -> Decimal:
        if hours <= self.rule.threshold_hours:
            return Decimal("0")
        overtime_hours = hours - self.rule.threshold_hours
        return base_rate * self.rule.multiplier * Decimal(overtime_hours)


@dataclass
class SickLeave:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    rule: SickLeaveRule = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def calculate_sick_pay(self, base_salary: Decimal, days: int) -> Decimal:
        if self.rule.max_days is not None and days > self.rule.max_days:
            days = self.rule.max_days
        return base_salary * (self.rule.percentage / Decimal("100")) * Decimal(days) / Decimal("30")
