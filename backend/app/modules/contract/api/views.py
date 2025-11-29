from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.modules.contract.domain.value_objects import ContractStatus, ContractType


class ContractTermsView(BaseModel):
    contract_type: ContractType
    rate_amount: Decimal
    rate_currency: str
    valid_from: date
    valid_to: Optional[date]
    hours_per_week: Optional[int]
    commission_percentage: Optional[Decimal]
    description: Optional[str]


class ContractListView(BaseModel):
    id: UUID
    employee_id: UUID
    contract_type: ContractType
    rate_amount: Decimal
    rate_currency: str
    valid_from: date
    valid_to: Optional[date]
    status: ContractStatus
    version: int


class ContractDetailView(BaseModel):
    id: UUID
    employee_id: UUID
    terms: ContractTermsView
    status: ContractStatus
    version: int
    cancellation_reason: Optional[str]
    canceled_at: Optional[date]
    created_at: Optional[date]
    updated_at: Optional[date]


class ContractListResponse(BaseModel):
    """Wrapper for list of contracts"""

    items: List[ContractListView]
    total: int
