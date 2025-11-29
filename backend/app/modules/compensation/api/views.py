from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.modules.compensation.domain.value_objects import BonusType, RateType


class RateView(BaseModel):
    id: UUID
    employee_id: UUID
    rate_type: RateType
    amount: Decimal
    currency: str
    valid_from: date
    valid_to: Optional[date]
    description: Optional[str]
    created_at: Optional[date]
    updated_at: Optional[date]


class BonusView(BaseModel):
    id: UUID
    employee_id: UUID
    bonus_type: BonusType
    amount: Decimal
    currency: str
    payment_date: date
    description: Optional[str]
    created_at: Optional[date]
    updated_at: Optional[date]


class RateListResponse(BaseModel):
    """Wrapper for list of rates"""

    items: List[RateView]
    total: int


class BonusListResponse(BaseModel):
    """Wrapper for list of bonuses"""

    items: List[BonusView]
    total: int
