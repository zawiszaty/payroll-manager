from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from app.modules.contract.domain.value_objects import ContractType


@dataclass
class CreateContractCommand:
    employee_id: UUID
    contract_type: ContractType
    rate_amount: Decimal
    rate_currency: str
    valid_from: date
    valid_to: Optional[date] = None
    hours_per_week: Optional[int] = None
    commission_percentage: Optional[Decimal] = None
    description: Optional[str] = None


@dataclass
class ActivateContractCommand:
    contract_id: UUID


@dataclass
class CancelContractCommand:
    contract_id: UUID
    reason: str


@dataclass
class ExpireContractCommand:
    contract_id: UUID
