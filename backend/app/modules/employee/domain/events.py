from datetime import date
from uuid import UUID

from app.shared.domain.events import DomainEvent


class EmployeeCreatedEvent(DomainEvent):
    employee_id: UUID
    first_name: str
    last_name: str
    email: str
    hire_date: date | None


class EmployeeUpdatedEvent(DomainEvent):
    employee_id: UUID
    old_values: dict
    new_values: dict


class EmployeeStatusChangedEvent(DomainEvent):
    employee_id: UUID
    old_status: str
    new_status: str
    status_valid_from: date
    status_valid_to: date | None
    reason: str | None
