from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class AbsenceType(str, Enum):
    VACATION = "vacation"
    SICK_LEAVE = "sick_leave"
    PARENTAL_LEAVE = "parental_leave"
    UNPAID_LEAVE = "unpaid_leave"
    BEREAVEMENT = "bereavement"
    STUDY_LEAVE = "study_leave"
    COMPASSIONATE = "compassionate"


class AbsenceStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class AbsenceBalanceInfo:
    absence_type: AbsenceType
    total_days: Decimal
    used_days: Decimal
    remaining_days: Decimal
    year: int

    def __post_init__(self):
        if self.total_days < 0:
            raise ValueError("Total days cannot be negative")
        if self.used_days < 0:
            raise ValueError("Used days cannot be negative")
        if self.used_days > self.total_days:
            raise ValueError("Used days cannot exceed total days")
        if self.year < 2000 or self.year > 2100:
            raise ValueError("Year must be between 2000 and 2100")
