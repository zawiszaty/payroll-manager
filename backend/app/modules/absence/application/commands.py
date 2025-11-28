from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.modules.absence.domain.value_objects import AbsenceType


@dataclass
class CreateAbsenceCommand:
    employee_id: UUID
    absence_type: AbsenceType
    start_date: date
    end_date: date
    reason: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ApproveAbsenceCommand:
    absence_id: UUID


@dataclass
class RejectAbsenceCommand:
    absence_id: UUID


@dataclass
class CancelAbsenceCommand:
    absence_id: UUID


@dataclass
class CreateAbsenceBalanceCommand:
    employee_id: UUID
    absence_type: AbsenceType
    year: int
    total_days: Decimal


@dataclass
class UpdateAbsenceBalanceCommand:
    balance_id: UUID
    total_days: Decimal
