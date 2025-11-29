"""
Contract Module Facade
Exposes contract module capabilities to other modules
This is the public interface for inter-module communication
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.contract.infrastructure.read_model import ContractReadModel


class ContractModuleFacade:
    """
    Facade for Contract module
    Provides async methods for other modules to query contract data
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.read_model = ContractReadModel(session)

    async def get_active_contract_for_employee(
        self, employee_id: UUID, check_date: date
    ):
        """
        Get active contract for employee on a specific date
        Returns the contract that is valid on the given date
        """
        contracts = await self.read_model.get_active_by_employee(employee_id)

        for contract in contracts:
            if contract.terms.valid_from <= check_date:
                if contract.terms.valid_to is None or contract.terms.valid_to >= check_date:
                    return contract

        return None

    async def has_active_contract(
        self, employee_id: UUID, check_date: date
    ) -> bool:
        """Check if employee has an active contract on the given date"""
        contract = await self.get_active_contract_for_employee(employee_id, check_date)
        return contract is not None

    async def get_contract_rate(
        self, employee_id: UUID, check_date: date
    ) -> Optional[Decimal]:
        """Get employee's contract rate for a specific date"""
        contract = await self.get_active_contract_for_employee(employee_id, check_date)
        if contract:
            return contract.terms.rate_amount
        return None

    async def get_contract_type(
        self, employee_id: UUID, check_date: date
    ) -> Optional[str]:
        """Get employee's contract type for a specific date"""
        contract = await self.get_active_contract_for_employee(employee_id, check_date)
        if contract:
            return contract.terms.contract_type.value
        return None

    async def get_contract_hours_per_week(
        self, employee_id: UUID, check_date: date
    ) -> Optional[int]:
        """Get contract hours per week (for hourly contracts)"""
        contract = await self.get_active_contract_for_employee(employee_id, check_date)
        if contract:
            return contract.terms.hours_per_week
        return None
