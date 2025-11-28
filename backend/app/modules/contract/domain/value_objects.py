from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional

from app.shared.domain.value_objects import DateRange, Money


class ContractType(str, Enum):
    FIXED_MONTHLY = "fixed_monthly"
    HOURLY = "hourly"
    B2B_DAILY = "b2b_daily"
    B2B_HOURLY = "b2b_hourly"
    TASK_BASED = "task_based"
    COMMISSION_BASED = "commission_based"


class ContractStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    PENDING = "pending"


@dataclass(frozen=True)
class ContractTerms:
    contract_type: ContractType
    rate: Money
    date_range: DateRange
    hours_per_week: Optional[int] = None
    commission_percentage: Optional[Decimal] = None
    description: Optional[str] = None

    def __post_init__(self):
        if self.contract_type in [ContractType.HOURLY, ContractType.B2B_HOURLY]:
            if self.hours_per_week is None or self.hours_per_week <= 0:
                raise ValueError("Hourly contracts must specify positive hours_per_week")

        if self.contract_type == ContractType.COMMISSION_BASED:
            if self.commission_percentage is None or self.commission_percentage <= 0:
                raise ValueError(
                    "Commission-based contracts must specify positive commission_percentage"
                )
