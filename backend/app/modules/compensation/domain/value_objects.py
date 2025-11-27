from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional
from app.shared.domain.value_objects import DateRange, Money


class RateType(str, Enum):
    BASE_SALARY = "base_salary"
    HOURLY_RATE = "hourly_rate"
    DAILY_RATE = "daily_rate"


class BonusType(str, Enum):
    PERFORMANCE = "performance"
    ANNUAL = "annual"
    SIGNING = "signing"
    RETENTION = "retention"
    PROJECT = "project"
    HOLIDAY = "holiday"


class DeductionType(str, Enum):
    TAX = "tax"
    INSURANCE = "insurance"
    PENSION = "pension"
    LOAN = "loan"
    OTHER = "other"


@dataclass(frozen=True)
class OvertimeRule:
    multiplier: Decimal
    threshold_hours: int
    date_range: DateRange

    def __post_init__(self):
        if self.multiplier <= Decimal("1.0"):
            raise ValueError("Overtime multiplier must be greater than 1.0")
        if self.threshold_hours <= 0:
            raise ValueError("Threshold hours must be positive")


@dataclass(frozen=True)
class SickLeaveRule:
    percentage: Decimal
    max_days: Optional[int]
    date_range: DateRange

    def __post_init__(self):
        if self.percentage <= 0 or self.percentage > 100:
            raise ValueError("Sick leave percentage must be between 0 and 100")
        if self.max_days is not None and self.max_days <= 0:
            raise ValueError("Max days must be positive if specified")
