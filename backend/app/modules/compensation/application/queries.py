from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass
class GetRateQuery:
    rate_id: UUID


@dataclass
class GetRatesByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetActiveRateQuery:
    employee_id: UUID
    check_date: date


@dataclass
class ListRatesQuery:
    page: int = 1
    limit: int = 100


@dataclass
class GetBonusQuery:
    bonus_id: UUID


@dataclass
class GetBonusesByEmployeeQuery:
    employee_id: UUID


@dataclass
class ListBonusesQuery:
    page: int = 1
    limit: int = 100


@dataclass
class GetDeductionQuery:
    deduction_id: UUID


@dataclass
class GetDeductionsByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetActiveDeductionsQuery:
    employee_id: UUID
    check_date: date


@dataclass
class GetOvertimeByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetSickLeaveByEmployeeQuery:
    employee_id: UUID
