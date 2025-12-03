from app.modules.contract.application.commands import (
    ActivateContractCommand,
    CancelContractCommand,
    CreateContractCommand,
    ExpireContractCommand,
)
from app.modules.contract.application.queries import (
    GetActiveContractsQuery,
    GetContractQuery,
    GetContractsByEmployeeQuery,
    ListContractsQuery,
)
from app.modules.contract.domain.models import Contract
from app.modules.contract.domain.repository import ContractRepository
from app.modules.contract.domain.services import (
    ActivateContractService,
    CancelContractService,
    CreateContractService,
    ExpireContractService,
)
from app.modules.contract.infrastructure.read_model import ContractReadModel


class CreateContractHandler:
    def __init__(self, repository: ContractRepository):
        self.repository = repository
        self.service = CreateContractService()

    async def handle(self, command: CreateContractCommand) -> Contract:
        contract = self.service.create(
            employee_id=command.employee_id,
            contract_type=command.contract_type,
            rate_amount=command.rate_amount,
            rate_currency=command.rate_currency,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
            hours_per_week=command.hours_per_week,
            commission_percentage=command.commission_percentage,
            description=command.description,
        )

        return await self.repository.save(contract)


class ActivateContractHandler:
    def __init__(self, repository: ContractRepository):
        self.repository = repository
        self.service = ActivateContractService()

    async def handle(self, command: ActivateContractCommand) -> Contract:
        contract = await self.repository.get_by_id(command.contract_id)
        if not contract:
            raise ValueError(f"Contract {command.contract_id} not found")

        contract = self.service.activate(contract)
        return await self.repository.save(contract)


class CancelContractHandler:
    def __init__(self, repository: ContractRepository):
        self.repository = repository
        self.service = CancelContractService()

    async def handle(self, command: CancelContractCommand) -> Contract:
        contract = await self.repository.get_by_id(command.contract_id)
        if not contract:
            raise ValueError(f"Contract {command.contract_id} not found")

        contract = self.service.cancel(contract, command.reason)
        return await self.repository.save(contract)


class ExpireContractHandler:
    def __init__(self, repository: ContractRepository):
        self.repository = repository
        self.service = ExpireContractService()

    async def handle(self, command: ExpireContractCommand) -> Contract:
        contract = await self.repository.get_by_id(command.contract_id)
        if not contract:
            raise ValueError(f"Contract {command.contract_id} not found")

        contract = self.service.expire(contract)
        return await self.repository.save(contract)


class GetContractHandler:
    def __init__(self, read_model: ContractReadModel):
        self.read_model = read_model

    async def handle(self, query: GetContractQuery):
        return await self.read_model.get_by_id(query.contract_id)


class GetContractsByEmployeeHandler:
    def __init__(self, read_model: ContractReadModel):
        self.read_model = read_model

    async def handle(self, query: GetContractsByEmployeeQuery):
        return await self.read_model.get_by_employee(query.employee_id)


class GetActiveContractsHandler:
    def __init__(self, read_model: ContractReadModel):
        self.read_model = read_model

    async def handle(self, query: GetActiveContractsQuery):
        return await self.read_model.get_active_by_employee(query.employee_id)


class ListContractsHandler:
    def __init__(self, read_model: ContractReadModel):
        self.read_model = read_model

    async def handle(self, query: ListContractsQuery):
        items, total_count = await self.read_model.list(skip=query.skip, limit=query.limit)
        return items, total_count
