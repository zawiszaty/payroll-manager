from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.modules.compensation.domain.value_objects import BonusType, DeductionType, RateType


@dataclass
class CreateRateCommand:
    employee_id: UUID
    rate_type: RateType
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: Optional[date] = None
    description: Optional[str] = None


@dataclass
class CreateBonusCommand:
    employee_id: UUID
    bonus_type: BonusType
    amount: Decimal
    currency: str
    payment_date: date
    description: Optional[str] = None


@dataclass
class CreateDeductionCommand:
    employee_id: UUID
    deduction_type: DeductionType
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: Optional[date] = None
    description: Optional[str] = None


@dataclass
class CreateOvertimeCommand:
    employee_id: UUID
    multiplier: Decimal
    threshold_hours: int
    valid_from: date
    valid_to: Optional[date] = None


@dataclass
class CreateSickLeaveCommand:
    employee_id: UUID
    percentage: Decimal
    max_days: Optional[int]
    valid_from: date
    valid_to: Optional[date] = None
