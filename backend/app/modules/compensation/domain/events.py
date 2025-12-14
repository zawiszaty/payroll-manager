from datetime import date
from decimal import Decimal
from uuid import UUID

from app.shared.domain.events import DomainEvent


class RateCreatedEvent(DomainEvent):
    rate_id: UUID
    employee_id: UUID
    rate_type: str
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: date | None


class BonusCreatedEvent(DomainEvent):
    bonus_id: UUID
    employee_id: UUID
    bonus_type: str
    amount: Decimal
    currency: str
    payment_date: date


class DeductionCreatedEvent(DomainEvent):
    deduction_id: UUID
    employee_id: UUID
    deduction_type: str
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: date | None


class OvertimeCreatedEvent(DomainEvent):
    overtime_id: UUID
    employee_id: UUID
    multiplier: Decimal
    threshold_hours: int
    valid_from: date
    valid_to: date | None


class SickLeaveCreatedEvent(DomainEvent):
    sick_leave_id: UUID
    employee_id: UUID
    percentage: Decimal
    max_days: int | None
    valid_from: date
    valid_to: date | None
