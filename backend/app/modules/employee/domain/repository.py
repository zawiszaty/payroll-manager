from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.employee.domain.models import Employee


class EmployeeRepository(ABC):
    @abstractmethod
    async def add(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    async def get_by_id(self, employee_id: UUID) -> Optional[Employee]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Employee]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        pass

    @abstractmethod
    async def update(self, employee: Employee) -> Employee:
        pass

    @abstractmethod
    async def delete(self, employee_id: UUID) -> bool:
        pass
