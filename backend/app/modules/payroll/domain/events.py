from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from app.modules.payroll.domain.value_objects import PayrollStatus
from app.shared.domain.events import DomainEvent


class PayrollCreatedEvent(DomainEvent):
    """Event raised when a new payroll is created"""

    payroll_id: UUID
    employee_id: UUID
    period_start: date
    period_end: date


class PayrollCalculatedEvent(DomainEvent):
    """Event raised when payroll calculations are completed"""

    payroll_id: UUID
    employee_id: UUID
    gross_pay: Decimal
    net_pay: Decimal


class PayrollApprovedEvent(DomainEvent):
    """Event raised when payroll is approved"""

    payroll_id: UUID
    employee_id: UUID
    approved_by: UUID
    approved_at: datetime


class PayrollProcessedEvent(DomainEvent):
    """Event raised when payroll is processed for payment"""

    payroll_id: UUID
    employee_id: UUID
    net_pay: Decimal
    processed_at: datetime


class PayrollPaidEvent(DomainEvent):
    """Event raised when payroll payment is completed"""

    payroll_id: UUID
    employee_id: UUID
    amount_paid: Decimal
    payment_reference: str
    paid_at: datetime


class PayrollStatusChangedEvent(DomainEvent):
    """Event raised when payroll status changes"""

    payroll_id: UUID
    old_status: PayrollStatus
    new_status: PayrollStatus


class MonthEndEvent(DomainEvent):
    """Event raised at the end of each month to trigger payroll calculations"""

    year: int
    month: int
    period_start: date
    period_end: date
