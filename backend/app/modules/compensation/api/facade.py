"""
Compensation Module Facade
Exposes compensation module capabilities to other modules
This is the public interface for inter-module communication
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.compensation.infrastructure.read_model import (
    BonusReadModel,
    RateReadModel,
)
from app.modules.compensation.presentation.views import BonusView, RateView


class ICompensationModuleFacade(ABC):
    """
    Interface for Compensation module facade
    Defines the public contract for inter-module communication
    """

    @abstractmethod
    async def get_active_rate(self, employee_id: UUID, check_date: date) -> RateView:
        """Get active compensation rate for employee on a specific date"""
        pass

    @abstractmethod
    async def get_bonuses_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[BonusView]:
        """
        Get all bonuses for employee within the given period
        Returns bonuses where payment_date is between start_date and end_date
        """
        pass

    @abstractmethod
    async def calculate_total_bonuses_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Decimal:
        """Calculate total bonus amount for the period"""
        pass

    @abstractmethod
    async def has_active_rate(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee has an active rate on the given date"""
        pass


class CompensationModuleFacade(ICompensationModuleFacade):
    """
    Facade for Compensation module
    Provides async methods for other modules to query compensation data
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.rate_read_model = RateReadModel(session)
        self.bonus_read_model = BonusReadModel(session)

    async def get_active_rate(self, employee_id: UUID, check_date: date) -> RateView:
        """Get active compensation rate for employee on a specific date"""
        return await self.rate_read_model.get_active_rate(employee_id, check_date)

    async def get_bonuses_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[BonusView]:
        """
        Get all bonuses for employee within the given period
        Returns bonuses where payment_date is between start_date and end_date
        """
        all_bonuses = await self.bonus_read_model.get_by_employee(employee_id)

        # Filter bonuses within the period
        period_bonuses = [
            bonus for bonus in all_bonuses if start_date <= bonus.payment_date <= end_date
        ]

        return period_bonuses

    async def calculate_total_bonuses_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> Decimal:
        """Calculate total bonus amount for the period"""
        bonuses = await self.get_bonuses_for_period(employee_id, start_date, end_date)
        return sum((bonus.amount for bonus in bonuses), Decimal("0"))

    async def has_active_rate(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee has an active rate on the given date"""
        rate = await self.get_active_rate(employee_id, check_date)
        return rate is not None
