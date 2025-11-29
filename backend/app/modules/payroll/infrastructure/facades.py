"""
Internal Payroll Module Facades
These facades wrap external module facades for use within Payroll module
They are used by PayrollDataGatheringAdapter to gather data from other modules
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.infrastructure.facade import AbsenceModuleFacade
from app.modules.compensation.infrastructure.facade import CompensationModuleFacade
from app.modules.contract.infrastructure.facade import ContractModuleFacade
from app.modules.employee.infrastructure.facade import EmployeeModuleFacade
from app.shared.domain.value_objects import Money


class EmployeeDataFacade:
    """
    Internal facade for accessing Employee module data
    Wraps EmployeeModuleFacade for use in payroll calculations
    """

    def __init__(self, session: AsyncSession):
        self.employee_facade = EmployeeModuleFacade(session)

    async def get_employee(self, employee_id: UUID) -> Any:
        """Get employee details"""
        return await self.employee_facade.get_employee_by_id(employee_id)

    async def is_active_on_date(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee is active on a specific date"""
        return await self.employee_facade.is_employee_active_on_date(
            employee_id, check_date
        )


class ContractDataFacade:
    """
    Internal facade for accessing Contract module data
    Wraps ContractModuleFacade for use in payroll calculations
    """

    def __init__(self, session: AsyncSession):
        self.contract_facade = ContractModuleFacade(session)

    async def has_active_contract(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee has active contract"""
        return await self.contract_facade.has_active_contract(employee_id, check_date)

    async def get_contract_data(
        self, employee_id: UUID, check_date: date
    ) -> Dict[str, Any]:
        """
        Get contract data for payroll calculation
        Returns a dictionary with contract details
        """
        contract = await self.contract_facade.get_active_contract_for_employee(
            employee_id, check_date
        )

        if not contract:
            return {}

        return {
            "contract_id": contract.id,
            "contract_type": contract.terms.contract_type.value,
            "rate_amount": contract.terms.rate_amount,
            "hours_per_week": contract.terms.hours_per_week,
            "valid_from": contract.terms.valid_from,
            "valid_to": contract.terms.valid_to,
        }


class CompensationDataFacade:
    """
    Internal facade for accessing Compensation module data
    Wraps CompensationModuleFacade for use in payroll calculations
    """

    def __init__(self, session: AsyncSession):
        self.compensation_facade = CompensationModuleFacade(session)

    async def get_bonuses_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[Any]:
        """Get bonuses for employee in a specific period"""
        return await self.compensation_facade.get_bonuses_for_period(
            employee_id, start_date, end_date
        )


class AbsenceDataFacade:
    """
    Internal facade for accessing Absence module data
    Wraps AbsenceModuleFacade for use in payroll calculations
    """

    def __init__(self, session: AsyncSession):
        self.absence_facade = AbsenceModuleFacade(session)

    async def get_absences_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[Any]:
        """Get approved absences for employee in a specific period"""
        return await self.absence_facade.get_approved_absences_in_period(
            employee_id, start_date, end_date
        )

    async def calculate_deduction(
        self, employee_id: UUID, start_date: date, end_date: date, daily_rate: Money
    ) -> Dict[str, Any]:
        """
        Calculate deduction for unpaid absences in period
        Returns dict with deduction_amount and absence_days
        """
        # Get deduction amount using the facade method
        deduction_amount = await self.absence_facade.calculate_unpaid_absence_deduction(
            employee_id, start_date, end_date, daily_rate.amount
        )

        # Get total absence days
        absence_days = await self.absence_facade.calculate_absence_days_in_period(
            employee_id, start_date, end_date
        )

        return {
            "deduction_amount": deduction_amount,
            "absence_days": absence_days,
        }
