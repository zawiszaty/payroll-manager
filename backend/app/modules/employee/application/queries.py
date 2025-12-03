from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetEmployeeQuery:
    employee_id: UUID


@dataclass
class ListEmployeesQuery:
    page: int = 1
    limit: int = 100


@dataclass
class GetEmployeeByEmailQuery:
    email: str
