"""
Absence Module Facade
Exposes absence module capabilities to other modules
This is the public interface for inter-module communication
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType
from app.modules.absence.infrastructure.repository import SQLAlchemyAbsenceRepository
from app.modules.absence.presentation.schemas import AbsenceResponse


class IAbsenceModuleFacade(ABC):
    """
    Interface for Absence module facade
    Defines the public contract for inter-module communication
    """

    @abstractmethod
    async def get_absences_for_employee(self, employee_id: UUID) -> List[AbsenceResponse]:
        """Get all absences for an employee"""
        pass

    @abstractmethod
    async def get_approved_absences_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[AbsenceResponse]:
        """
        Get all approved absences for employee that overlap with the given period
        Returns absences where status is APPROVED and dates overlap with the period
        """
        pass

    @abstractmethod
    async def calculate_absence_days_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> int:
        """
        Calculate total absence days within the period
        Only counts approved absences
        """
        pass

    @abstractmethod
    async def calculate_unpaid_absence_deduction(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        daily_rate: Decimal,
    ) -> Decimal:
        """
        Calculate deduction amount for unpaid absences in the period
        Only UNPAID_LEAVE type absences result in deductions
        """
        pass

    @abstractmethod
    async def has_absences_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> bool:
        """Check if employee has any approved absences in the period"""
        pass


class AbsenceModuleFacade(IAbsenceModuleFacade):
    """
    Facade for Absence module
    Provides async methods for other modules to query absence data
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SQLAlchemyAbsenceRepository(session)

    async def get_absences_for_employee(self, employee_id: UUID) -> List[AbsenceResponse]:
        """Get all absences for an employee"""
        absences = await self.repository.get_by_employee(employee_id)

        return [
            AbsenceResponse(
                id=absence.id,
                employee_id=absence.employee_id,
                absence_type=absence.absence_type,
                start_date=absence.period.start_date,
                end_date=absence.period.end_date,
                status=absence.status,
                reason=absence.reason,
                notes=absence.notes,
            )
            for absence in absences
        ]

    async def get_approved_absences_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[AbsenceResponse]:
        """
        Get all approved absences for employee that overlap with the given period
        Returns absences where status is APPROVED and dates overlap with the period
        """
        all_absences = await self.get_absences_for_employee(employee_id)

        # Filter absences that overlap with the period and are approved
        period_absences = []
        for absence in all_absences:
            # Check if absence overlaps with the period
            if absence.start_date <= end_date and absence.end_date >= start_date:
                # Check if absence is approved
                if absence.status == AbsenceStatus.APPROVED:
                    period_absences.append(absence)

        return period_absences

    async def calculate_absence_days_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> int:
        """
        Calculate total absence days within the period
        Only counts approved absences
        """
        absences = await self.get_approved_absences_in_period(employee_id, start_date, end_date)

        total_days = 0
        for absence in absences:
            # Calculate days within the period boundaries
            absence_start = max(absence.start_date, start_date)
            absence_end = min(absence.end_date, end_date)
            days = (absence_end - absence_start).days + 1
            total_days += days

        return total_days

    async def calculate_unpaid_absence_deduction(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        daily_rate: Decimal,
    ) -> Decimal:
        """
        Calculate deduction amount for unpaid absences in the period
        Only UNPAID_LEAVE type absences result in deductions
        """
        absences = await self.get_approved_absences_in_period(employee_id, start_date, end_date)

        total_deduction = Decimal("0")
        for absence in absences:
            # Only deduct for unpaid absence types
            if absence.absence_type == AbsenceType.UNPAID_LEAVE:
                # Calculate days within the period
                absence_start = max(absence.start_date, start_date)
                absence_end = min(absence.end_date, end_date)
                days = (absence_end - absence_start).days + 1

                total_deduction += daily_rate * Decimal(days)

        return total_deduction

    async def has_absences_in_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> bool:
        """Check if employee has any approved absences in the period"""
        absences = await self.get_approved_absences_in_period(employee_id, start_date, end_date)
        return len(absences) > 0
