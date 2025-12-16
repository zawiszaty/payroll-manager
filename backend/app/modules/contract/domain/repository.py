from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from uuid import UUID

from app.modules.contract.domain.models import Contract


class ContractRepository(ABC):
    @abstractmethod
    async def save(self, contract: Contract, event_type: str | None = None) -> Contract:
        pass

    @abstractmethod
    async def get_by_id(self, contract_id: UUID) -> Optional[Contract]:
        pass

    @abstractmethod
    async def get_by_employee_id(self, employee_id: UUID) -> List[Contract]:
        pass

    @abstractmethod
    async def get_active_contracts(self, employee_id: UUID) -> List[Contract]:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Contract]:
        pass

    @abstractmethod
    async def delete(self, contract_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_expired_contracts(self, check_date: date) -> List[Contract]:
        """
        Get all ACTIVE contracts where valid_to < check_date.
        A contract is expired when the check_date is after its last valid day.
        This query should be performed at the database level for scalability.
        """
        pass
