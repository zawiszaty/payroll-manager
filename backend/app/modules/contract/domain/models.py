from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from app.modules.contract.domain.value_objects import ContractStatus, ContractTerms


@dataclass
class Contract:
    id: UUID = field(default_factory=uuid4)
    employee_id: UUID = field(default_factory=uuid4)
    terms: ContractTerms | None = None
    status: ContractStatus = ContractStatus.PENDING
    version: int = 1
    cancellation_reason: Optional[str] = None
    canceled_at: Optional[date] = None
    created_at: date = field(default_factory=date.today)
    updated_at: date = field(default_factory=date.today)

    def activate(self) -> None:
        if self.status == ContractStatus.ACTIVE:
            raise ValueError("Contract is already active")
        if self.status in [ContractStatus.EXPIRED, ContractStatus.CANCELED]:
            raise ValueError(f"Cannot activate {self.status.value} contract")

        self.status = ContractStatus.ACTIVE
        self.updated_at = date.today()

    def cancel(self, reason: str) -> None:
        if self.status != ContractStatus.ACTIVE:
            raise ValueError(f"Cannot cancel contract with status {self.status.value}")

        self.status = ContractStatus.CANCELED
        self.cancellation_reason = reason
        self.canceled_at = date.today()
        self.updated_at = date.today()

    def expire(self) -> None:
        if self.status != ContractStatus.ACTIVE:
            raise ValueError(f"Cannot expire contract with status {self.status.value}")

        self.status = ContractStatus.EXPIRED
        self.updated_at = date.today()

    def is_active_at(self, check_date: date) -> bool:
        if self.status != ContractStatus.ACTIVE:
            return False
        if self.terms is None:
            return False
        return self.terms.date_range.is_active_at(check_date)

    def is_expired_at(self, check_date: date) -> bool:
        if self.terms is None or self.terms.date_range.valid_to is None:
            return False
        return check_date > self.terms.date_range.valid_to
