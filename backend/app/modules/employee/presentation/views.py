from datetime import date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.modules.employee.domain.value_objects import EmploymentStatusType


class EmploymentStatusView(BaseModel):
    status_type: EmploymentStatusType
    valid_from: date
    valid_to: Optional[date]
    reason: Optional[str]


class EmployeeListView(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    hire_date: Optional[date]
    current_status: Optional[EmploymentStatusType]


class EmployeeDetailView(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    date_of_birth: Optional[date]
    hire_date: Optional[date]
    statuses: List[EmploymentStatusView]
    created_at: Optional[date]
    updated_at: Optional[date]


class EmployeeListResponse(BaseModel):
    """Wrapper for list of employees"""

    items: List[EmployeeListView]
    total: int
