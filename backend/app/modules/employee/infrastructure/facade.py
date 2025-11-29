"""
Employee Module Facade
Exposes employee module capabilities to other modules
This is the public interface for inter-module communication
"""

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.employee.domain.value_objects import EmploymentStatusType
from app.modules.employee.infrastructure.read_model import EmployeeReadModel


class EmployeeModuleFacade:
    """
    Facade for Employee module
    Provides async methods for other modules to query employee data
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.read_model = EmployeeReadModel(session)

    async def get_employee_by_id(self, employee_id: UUID):
        """Get employee details by ID"""
        return await self.read_model.get_by_id(employee_id)

    async def is_employee_active_on_date(
        self, employee_id: UUID, check_date: date
    ) -> bool:
        """
        Check if employee is active on a specific date
        Returns True if employee has an ACTIVE status on that date
        """
        employee = await self.get_employee_by_id(employee_id)
        if not employee:
            return False

        # Check if employee has an active status on the date
        for status in employee.statuses:
            if status.valid_from <= check_date:
                if status.valid_to is None or status.valid_to >= check_date:
                    return status.status_type == EmploymentStatusType.ACTIVE

        return False

    async def get_employee_hire_date(self, employee_id: UUID) -> Optional[date]:
        """Get employee hire date"""
        employee = await self.get_employee_by_id(employee_id)
        return employee.hire_date if employee else None

    async def get_employee_full_name(self, employee_id: UUID) -> Optional[str]:
        """Get employee full name"""
        employee = await self.get_employee_by_id(employee_id)
        if employee:
            return f"{employee.first_name} {employee.last_name}"
        return None
