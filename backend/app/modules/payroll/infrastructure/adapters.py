"""
Payroll Module Adapters
These adapters use internal facades to provide high-level operations
Adapters coordinate multiple facade calls to implement business operations
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payroll.domain.value_objects import AbsenceImpact, PayrollDataCollection
from app.modules.payroll.infrastructure.facades import (
    AbsenceDataFacade,
    CompensationDataFacade,
    ContractDataFacade,
    EmployeeDataFacade,
    TimesheetDataFacade,
)
from app.shared.domain.value_objects import Money


class IPayrollDataGatheringAdapter(ABC):
    """
    Interface for Payroll Data Gathering Adapter
    Defines the contract for gathering payroll data from multiple modules
    """

    @abstractmethod
    async def validate_payroll_eligibility(self, employee_id: UUID, check_date: date) -> bool:
        """
        Validate if payroll can be processed for employee
        Coordinates validation across Employee and Contract modules
        """
        pass

    @abstractmethod
    async def gather_all_payroll_data(
        self, employee_id: UUID, period_start: date, period_end: date
    ) -> PayrollDataCollection:
        """
        Main orchestration method that gathers all data needed for payroll
        Uses all internal facades to collect data from multiple modules
        """
        pass

    @abstractmethod
    async def calculate_absence_impact(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        daily_rate: Money,
    ) -> AbsenceImpact:
        """
        Calculate absence impact for payroll
        Delegates to AbsenceDataFacade
        """
        pass


class PayrollDataGatheringAdapter(IPayrollDataGatheringAdapter):
    """
    Adapter for gathering payroll data from multiple modules
    Uses internal facades to coordinate data collection
    This is used by domain services for payroll calculation
    """

    def __init__(self, session: AsyncSession):
        self.session = session

        # Initialize internal facades
        self.employee_facade = EmployeeDataFacade(session)
        self.contract_facade = ContractDataFacade(session)
        self.compensation_facade = CompensationDataFacade(session)
        self.absence_facade = AbsenceDataFacade(session)
        self.timesheet_facade = TimesheetDataFacade(session)

    async def validate_payroll_eligibility(self, employee_id: UUID, check_date: date) -> bool:
        """
        Validate if payroll can be processed for employee
        Coordinates validation across Employee and Contract modules
        """
        # Check employee is active
        is_active = await self.employee_facade.is_active_on_date(employee_id, check_date)
        if not is_active:
            return False

        # Check has active contract
        has_contract = await self.contract_facade.has_active_contract(employee_id, check_date)
        return has_contract

    async def gather_all_payroll_data(
        self, employee_id: UUID, period_start: date, period_end: date
    ) -> PayrollDataCollection:
        """
        Main orchestration method that gathers all data needed for payroll
        Uses all internal facades to collect data from multiple modules
        """
        # Get data from each module via facades
        employee = await self.employee_facade.get_employee(employee_id)
        contract_data = await self.contract_facade.get_contract_data(employee_id, period_start)
        bonuses = await self.compensation_facade.get_bonuses_for_period(
            employee_id, period_start, period_end
        )
        absences = await self.absence_facade.get_absences_for_period(
            employee_id, period_start, period_end
        )
        timesheets = await self.timesheet_facade.get_approved_timesheets_for_period(
            employee_id, period_start, period_end
        )

        return PayrollDataCollection(
            employee=employee,
            contract_data=contract_data,
            bonuses=bonuses,
            absences=absences,
            timesheets=timesheets,
        )

    async def calculate_absence_impact(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        daily_rate: Money,
    ) -> AbsenceImpact:
        """
        Calculate absence impact for payroll
        Delegates to AbsenceDataFacade
        """
        result = await self.absence_facade.calculate_deduction(
            employee_id, start_date, end_date, daily_rate
        )
        return AbsenceImpact(
            deduction_amount=Money(result["deduction_amount"], daily_rate.currency),
            absence_days=result["absence_days"],
        )


class IPayrollValidationAdapter(ABC):
    """
    Interface for Payroll Validation Adapter
    Defines the contract for payroll validation operations
    """

    @abstractmethod
    async def can_create_payroll(self, employee_id: UUID, check_date: date) -> tuple[bool, str]:
        """
        Validate if new payroll can be created
        Returns (can_create, reason) tuple
        """
        pass

    @abstractmethod
    async def validate_payroll_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> tuple[bool, str]:
        """
        Validate payroll period for employee
        Ensures employee has contract coverage for entire period
        """
        pass


class PayrollValidationAdapter(IPayrollValidationAdapter):
    """
    Adapter for payroll validation operations
    Uses facades to perform validation checks
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.employee_facade = EmployeeDataFacade(session)
        self.contract_facade = ContractDataFacade(session)

    async def can_create_payroll(self, employee_id: UUID, check_date: date) -> tuple[bool, str]:
        """
        Validate if new payroll can be created
        Returns (can_create, reason) tuple
        """
        # Check employee exists and is active
        is_active = await self.employee_facade.is_active_on_date(employee_id, check_date)
        if not is_active:
            return False, "Employee is not active on the specified date"

        # Check has active contract
        has_contract = await self.contract_facade.has_active_contract(employee_id, check_date)
        if not has_contract:
            return False, "Employee has no active contract on the specified date"

        return True, ""

    async def validate_payroll_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> tuple[bool, str]:
        """
        Validate payroll period for employee
        Ensures employee has contract coverage for entire period
        """
        # Check start date
        has_contract_start = await self.contract_facade.has_active_contract(employee_id, start_date)
        if not has_contract_start:
            return False, "No active contract at period start"

        # Check end date
        has_contract_end = await self.contract_facade.has_active_contract(employee_id, end_date)
        if not has_contract_end:
            return False, "No active contract at period end"

        return True, ""
