from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class DateRange:
    valid_from: date
    valid_to: Optional[date] = None

    def __post_init__(self):
        if self.valid_to and self.valid_from > self.valid_to:
            raise ValueError("valid_from must be before valid_to")

    @property
    def start_date(self) -> date:
        return self.valid_from

    @property
    def end_date(self) -> Optional[date]:
        return self.valid_to

    def contains(self, check_date: date) -> bool:
        return self.is_active_at(check_date)

    def is_active_at(self, check_date: date) -> bool:
        if check_date < self.valid_from:
            return False
        if self.valid_to and check_date > self.valid_to:
            return False
        return True

    def overlaps_with(self, other: "DateRange") -> bool:
        if self.valid_to and other.valid_from > self.valid_to:
            return False
        if other.valid_to and self.valid_from > other.valid_to:
            return False
        return True


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
