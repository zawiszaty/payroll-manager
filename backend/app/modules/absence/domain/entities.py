from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType
from app.shared.domain.value_objects import DateRange


class Absence:
    def __init__(
        self,
        employee_id: UUID,
        absence_type: AbsenceType,
        period: DateRange,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        id: Optional[UUID] = None,
        status: AbsenceStatus = AbsenceStatus.PENDING,
    ):
        self.id = id or uuid4()
        self.employee_id = employee_id
        self.absence_type = absence_type
        self.period = period
        self.reason = reason
        self.notes = notes
        self.status = status

        self._validate()

    def _validate(self):
        if self.period.start_date > self.period.end_date:
            raise ValueError("Start date must be before or equal to end date")

    def calculate_days(self) -> Decimal:
        delta = self.period.end_date - self.period.start_date
        return Decimal(str(delta.days + 1))

    def approve(self):
        if self.status != AbsenceStatus.PENDING:
            raise ValueError(f"Cannot approve absence with status {self.status}")
        self.status = AbsenceStatus.APPROVED

    def reject(self):
        if self.status != AbsenceStatus.PENDING:
            raise ValueError(f"Cannot reject absence with status {self.status}")
        self.status = AbsenceStatus.REJECTED

    def cancel(self):
        if self.status not in [AbsenceStatus.PENDING, AbsenceStatus.APPROVED]:
            raise ValueError(f"Cannot cancel absence with status {self.status}")
        self.status = AbsenceStatus.CANCELLED

    def is_active_at(self, check_date: date) -> bool:
        return (
            self.status == AbsenceStatus.APPROVED
            and self.period.contains(check_date)
        )

    def overlaps_with(self, other_period: DateRange) -> bool:
        return self.period.overlaps_with(other_period)


class AbsenceBalance:
    def __init__(
        self,
        employee_id: UUID,
        absence_type: AbsenceType,
        year: int,
        total_days: Decimal,
        used_days: Decimal = Decimal("0"),
        id: Optional[UUID] = None,
    ):
        self.id = id or uuid4()
        self.employee_id = employee_id
        self.absence_type = absence_type
        self.year = year
        self.total_days = total_days
        self.used_days = used_days

        self._validate()

    def _validate(self):
        if self.total_days < 0:
            raise ValueError("Total days cannot be negative")
        if self.used_days < 0:
            raise ValueError("Used days cannot be negative")
        if self.year < 2000 or self.year > 2100:
            raise ValueError("Year must be between 2000 and 2100")

    def remaining_days(self) -> Decimal:
        return self.total_days - self.used_days

    def can_take_absence(self, days: Decimal) -> bool:
        return self.remaining_days() >= days

    def use_days(self, days: Decimal):
        if days < 0:
            raise ValueError("Days to use must be positive")
        if not self.can_take_absence(days):
            raise ValueError(
                f"Insufficient balance. Requested: {days}, Available: {self.remaining_days()}"
            )
        self.used_days += days

    def return_days(self, days: Decimal):
        if days < 0:
            raise ValueError("Days to return must be positive")
        if days > self.used_days:
            raise ValueError("Cannot return more days than used")
        self.used_days -= days

    def set_total_days(self, total_days: Decimal):
        if total_days < 0:
            raise ValueError("Total days cannot be negative")
        self.total_days = total_days
