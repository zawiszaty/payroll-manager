"""Domain events for absence module"""

from datetime import date
from uuid import UUID

from app.shared.domain.events import DomainEvent


class AbsenceCreatedEvent(DomainEvent):
    """Event raised when an absence is created"""

    absence_id: UUID
    employee_id: UUID
    absence_type: str
    start_date: date
    end_date: date
    reason: str | None
    status: str


class AbsenceApprovedEvent(DomainEvent):
    """Event raised when an absence is approved"""

    absence_id: UUID
    employee_id: UUID
    absence_type: str
    start_date: date
    end_date: date
    approved_by: UUID | None


class AbsenceRejectedEvent(DomainEvent):
    """Event raised when an absence is rejected"""

    absence_id: UUID
    employee_id: UUID
    absence_type: str
    start_date: date
    end_date: date
    rejected_by: UUID | None


class AbsenceCancelledEvent(DomainEvent):
    """Event raised when an absence is cancelled"""

    absence_id: UUID
    employee_id: UUID
    absence_type: str
    start_date: date
    end_date: date
    was_approved: bool
    cancelled_by: UUID | None
