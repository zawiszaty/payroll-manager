from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

from app.shared.domain.value_objects import DateRange


class EmploymentStatusType(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class EmploymentStatus:
    status_type: EmploymentStatusType
    date_range: DateRange
    reason: Optional[str] = None

    def is_active_at(self, check_date: date) -> bool:
        return self.date_range.is_active_at(check_date)
