from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from app.modules.absence.domain.entities import Absence, AbsenceBalance
from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType


class AbsenceRepository(ABC):
    @abstractmethod
    async def save(self, absence: Absence) -> Absence:
        pass

    @abstractmethod
    async def get_by_id(self, absence_id: UUID) -> Optional[Absence]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Absence], int]:
        pass

    @abstractmethod
    async def get_by_employee(self, employee_id: UUID) -> List[Absence]:
        pass

    @abstractmethod
    async def get_by_employee_and_status(
        self, employee_id: UUID, status: AbsenceStatus
    ) -> List[Absence]:
        pass

    @abstractmethod
    async def get_approved_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[Absence]:
        pass


class AbsenceBalanceRepository(ABC):
    @abstractmethod
    async def save(self, balance: AbsenceBalance) -> AbsenceBalance:
        pass

    @abstractmethod
    async def get_by_id(self, balance_id: UUID) -> Optional[AbsenceBalance]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[AbsenceBalance], int]:
        pass

    @abstractmethod
    async def get_by_employee(self, employee_id: UUID) -> List[AbsenceBalance]:
        pass

    @abstractmethod
    async def get_by_employee_and_year(self, employee_id: UUID, year: int) -> List[AbsenceBalance]:
        pass

    @abstractmethod
    async def get_by_employee_type_year(
        self, employee_id: UUID, absence_type: AbsenceType, year: int
    ) -> Optional[AbsenceBalance]:
        pass
