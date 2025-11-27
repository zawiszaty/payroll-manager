from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID

from app.modules.employee.domain.value_objects import EmploymentStatusType


@dataclass
class CreateEmployeeCommand:
    first_name: str
    last_name: str
    email: str
    hire_date: date
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


@dataclass
class UpdateEmployeeCommand:
    employee_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


@dataclass
class ChangeEmployeeStatusCommand:
    employee_id: UUID
    new_status: EmploymentStatusType
    effective_date: date
    reason: Optional[str] = None
