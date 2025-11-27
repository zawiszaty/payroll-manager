from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetContractQuery:
    contract_id: UUID


@dataclass
class GetContractsByEmployeeQuery:
    employee_id: UUID


@dataclass
class GetActiveContractsQuery:
    employee_id: UUID


@dataclass
class ListContractsQuery:
    skip: int = 0
    limit: int = 100
