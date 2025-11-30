"""
Compensation Module Adapters
Anti-Corruption Layer for external module dependencies
"""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.modules.employee.api.facade import IEmployeeModuleFacade


class IEmployeeAdapter(ABC):
    """
    Interface for Employee adapter
    Defines the contract for employee validation services
    """

    @abstractmethod
    async def validate_employee_exists(self, employee_id: UUID) -> None:
        """
        Validate that employee exists
        Raises ValueError if employee not found
        """
        pass

    @abstractmethod
    async def get_employee_full_name(self, employee_id: UUID) -> str | None:
        """Get employee's full name"""
        pass

    @abstractmethod
    async def is_employee_active(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee is active on given date"""
        pass


class EmployeeAdapter(IEmployeeAdapter):
    """
    Adapter for Employee module
    Provides employee validation services for compensation operations
    """

    def __init__(self, employee_facade: IEmployeeModuleFacade):
        self.employee_facade = employee_facade

    async def validate_employee_exists(self, employee_id: UUID) -> None:
        """
        Validate that employee exists
        Raises ValueError if employee not found
        """
        employee = await self.employee_facade.get_employee_by_id(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")

    async def get_employee_full_name(self, employee_id: UUID) -> str | None:
        """Get employee's full name"""
        return await self.employee_facade.get_employee_full_name(employee_id)

    async def is_employee_active(self, employee_id: UUID, check_date: date) -> bool:
        """Check if employee is active on given date"""
        return await self.employee_facade.is_employee_active_on_date(employee_id, check_date)
