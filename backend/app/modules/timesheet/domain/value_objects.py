from dataclasses import dataclass
from enum import Enum


class TimesheetStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class OvertimeType(Enum):
    REGULAR = "regular"
    WEEKEND = "weekend"
    HOLIDAY = "holiday"
    NIGHT_SHIFT = "night_shift"


@dataclass(frozen=True)
class TimeEntry:
    hours: float
    overtime_hours: float
    overtime_type: OvertimeType | None

    def __post_init__(self) -> None:
        if self.hours < 0:
            raise ValueError("Hours cannot be negative")
        if self.overtime_hours < 0:
            raise ValueError("Overtime hours cannot be negative")
        if self.overtime_hours > 0 and self.overtime_type is None:
            raise ValueError("Overtime type required when overtime hours > 0")
        if self.overtime_hours == 0 and self.overtime_type is not None:
            raise ValueError("Overtime type should be None when no overtime hours")

    @property
    def total_hours(self) -> float:
        return self.hours + self.overtime_hours
