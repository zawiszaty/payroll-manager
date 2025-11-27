from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetEmployeeQuery:
    employee_id: UUID


@dataclass
class ListEmployeesQuery:
    skip: int = 0
    limit: int = 100


@dataclass
class GetEmployeeByEmailQuery:
    email: str
