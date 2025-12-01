from dataclasses import dataclass
from enum import Enum


class AuditAction(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STATUS_CHANGED = "status_changed"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELED = "canceled"
    ACTIVATED = "activated"
    EXPIRED = "expired"
    CALCULATED = "calculated"
    PROCESSED = "processed"
    PAID = "paid"
    COMPLETED = "completed"
    FAILED = "failed"


class EntityType(Enum):
    EMPLOYEE = "employee"
    CONTRACT = "contract"
    PAYROLL = "payroll"
    ABSENCE = "absence"
    ABSENCE_BALANCE = "absence_balance"
    RATE = "rate"
    BONUS = "bonus"
    DEDUCTION = "deduction"
    OVERTIME = "overtime"
    SICK_LEAVE = "sick_leave"
    REPORT = "report"
    TIMESHEET = "timesheet"


@dataclass(frozen=True)
class AuditMetadata:
    event_type: str
    event_data: dict
