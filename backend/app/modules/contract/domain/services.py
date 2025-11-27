from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID
from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.value_objects import ContractTerms, ContractStatus, ContractType
from app.shared.domain.value_objects import DateRange, Money


class CreateContractService:
    def create(
        self,
        employee_id: UUID,
        contract_type: ContractType,
        rate_amount: Decimal,
        rate_currency: str,
        valid_from: date,
        valid_to: Optional[date] = None,
        hours_per_week: Optional[int] = None,
        commission_percentage: Optional[Decimal] = None,
        description: Optional[str] = None,
    ) -> Contract:
        terms = ContractTerms(
            contract_type=contract_type,
            rate=Money(amount=rate_amount, currency=rate_currency),
            date_range=DateRange(valid_from=valid_from, valid_to=valid_to),
            hours_per_week=hours_per_week,
            commission_percentage=commission_percentage,
            description=description,
        )

        contract = Contract(
            employee_id=employee_id,
            terms=terms,
            status=ContractStatus.PENDING,
        )

        return contract


class CancelContractService:
    def cancel(self, contract: Contract, reason: str) -> Contract:
        contract.cancel(reason)
        return contract


class ExpireContractService:
    def expire(self, contract: Contract) -> Contract:
        contract.expire()
        return contract


class ActivateContractService:
    def activate(self, contract: Contract) -> Contract:
        contract.activate()
        return contract
