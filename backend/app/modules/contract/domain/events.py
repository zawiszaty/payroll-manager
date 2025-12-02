from datetime import date
from decimal import Decimal
from uuid import UUID

from app.shared.domain.events import DomainEvent


class ContractCreatedEvent(DomainEvent):
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    rate_amount: Decimal
    rate_currency: str
    valid_from: date
    valid_to: date | None


class ContractActivatedEvent(DomainEvent):
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    activated_at: date


class ContractCanceledEvent(DomainEvent):
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    cancellation_reason: str
    canceled_at: date


class ContractExpiredEvent(DomainEvent):
    contract_id: UUID
    employee_id: UUID
    contract_type: str
    expired_at: date
