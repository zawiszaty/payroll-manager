from dataclasses import dataclass
from uuid import UUID

from app.modules.absence.domain.value_objects import AbsenceStatus


@dataclass
class GetAbsenceQuery:
    absence_id: UUID


@dataclass
class ListAbsencesQuery:
    pass


@dataclass
class GetAbsencesByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetAbsencesByEmployeeAndStatusQuery:
    employee_id: UUID
    status: AbsenceStatus


@dataclass
class GetAbsenceBalanceQuery:
    balance_id: UUID


@dataclass
class ListAbsenceBalancesQuery:
    pass


@dataclass
class GetAbsenceBalancesByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetAbsenceBalancesByEmployeeAndYearQuery:
    employee_id: UUID
    year: int
