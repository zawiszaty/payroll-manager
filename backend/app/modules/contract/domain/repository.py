from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.modules.contract.domain.models import Contract


class ContractRepository(ABC):
    @abstractmethod
    async def add(self, contract: Contract) -> Contract:
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
    async def update(self, contract: Contract) -> Contract:
        pass

    @abstractmethod
    async def delete(self, contract_id: UUID) -> bool:
        pass
