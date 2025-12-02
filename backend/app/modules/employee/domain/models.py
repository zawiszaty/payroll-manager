from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from uuid import UUID, uuid4

from app.modules.employee.domain.value_objects import EmploymentStatus, EmploymentStatusType
from app.shared.domain.events import DomainEvent


@dataclass
class Employee:
    id: UUID = field(default_factory=uuid4)
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    hire_date: Optional[date] = None
    statuses: List[EmploymentStatus] = field(default_factory=list)
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False, repr=False)

    def add_status(self, status: EmploymentStatus) -> None:
        for existing_status in self.statuses:
            if existing_status.date_range.overlaps_with(status.date_range):
                raise ValueError("Status periods cannot overlap")
        self.statuses.append(status)
        self.updated_at = date.today()

    def get_status_at(self, check_date: date) -> Optional[EmploymentStatus]:
        for status in self.statuses:
            if status.is_active_at(check_date):
                return status
        return None

    def is_active_at(self, check_date: date) -> bool:
        status = self.get_status_at(check_date)
        return status is not None and status.status_type == EmploymentStatusType.ACTIVE

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def _add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        self._domain_events.clear()
