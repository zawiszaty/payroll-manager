from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetPayrollQuery:
    payroll_id: UUID


@dataclass
class ListPayrollsQuery:
    page: int = 1
    limit: int = 100


@dataclass
class ListPayrollsByEmployeeQuery:
    employee_id: UUID
    page: int = 1
    limit: int = 100
