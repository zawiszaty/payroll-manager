from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetPayrollQuery:
    payroll_id: UUID


@dataclass
class ListPayrollsQuery:
    skip: int = 0
    limit: int = 100


@dataclass
class ListPayrollsByEmployeeQuery:
    employee_id: UUID
    skip: int = 0
    limit: int = 100
