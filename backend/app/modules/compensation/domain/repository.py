from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from app.modules.compensation.domain.models import Bonus, Deduction, Overtime, Rate, SickLeave


class RateRepository(ABC):
    @abstractmethod
    async def save(self, rate: Rate) -> Rate:
        pass

    @abstractmethod
    async def get_by_id(self, rate_id: UUID) -> Optional[Rate]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[Rate]:
        pass

    @abstractmethod
    async def get_active_rate(self, employee_id: UUID, check_date: date) -> Optional[Rate]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Rate]:
        pass

    @abstractmethod
    async def delete(self, rate_id: UUID) -> bool:
        pass


class BonusRepository(ABC):
    @abstractmethod
    async def save(self, bonus: Bonus) -> Bonus:
        pass

    @abstractmethod
    async def get_by_id(self, bonus_id: UUID) -> Optional[Bonus]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[Bonus]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Bonus]:
        pass

    @abstractmethod
    async def delete(self, bonus_id: UUID) -> bool:
        pass


class DeductionRepository(ABC):
    @abstractmethod
    async def save(self, deduction: Deduction) -> Deduction:
        pass

    @abstractmethod
    async def get_by_id(self, deduction_id: UUID) -> Optional[Deduction]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[Deduction]:
        pass

    @abstractmethod
    async def get_active_deductions(self, employee_id: UUID, check_date: date) -> List[Deduction]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Deduction]:
        pass

    @abstractmethod
    async def delete(self, deduction_id: UUID) -> bool:
        pass


class OvertimeRepository(ABC):
    @abstractmethod
    async def save(self, overtime: Overtime) -> Overtime:
        pass

    @abstractmethod
    async def get_by_id(self, overtime_id: UUID) -> Optional[Overtime]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[Overtime]:
        pass

    @abstractmethod
    async def delete(self, overtime_id: UUID) -> bool:
        pass


class SickLeaveRepository(ABC):
    @abstractmethod
    async def save(self, sick_leave: SickLeave) -> SickLeave:
        pass

    @abstractmethod
    async def get_by_id(self, sick_leave_id: UUID) -> Optional[SickLeave]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[SickLeave]:
        pass

    @abstractmethod
    async def delete(self, sick_leave_id: UUID) -> bool:
        pass
