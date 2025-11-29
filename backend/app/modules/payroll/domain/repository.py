from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.payroll.domain.models import Payroll


class PayrollRepository(ABC):
    """Repository interface for Payroll aggregate"""

    @abstractmethod
    async def save(self, payroll: Payroll) -> Payroll:
        """Save payroll (insert or update)"""
        pass

    @abstractmethod
    async def get_by_id(self, payroll_id: UUID) -> Optional[Payroll]:
        """Get payroll by ID"""
        pass

    @abstractmethod
    async def get_by_employee(self, employee_id: UUID) -> List[Payroll]:
        """Get all payrolls for an employee"""
        pass

    @abstractmethod
    async def delete(self, payroll_id: UUID) -> None:
        """Delete a payroll"""
        pass
