from typing import List

from app.modules.compensation.application.commands import (
    CreateBonusCommand,
    CreateDeductionCommand,
    CreateOvertimeCommand,
    CreateRateCommand,
    CreateSickLeaveCommand,
)
from app.modules.compensation.application.queries import (
    GetActiveDeductionsQuery,
    GetActiveRateQuery,
    GetBonusesByEmployeeQuery,
    GetBonusQuery,
    GetDeductionsByEmployeeQuery,
    GetOvertimeByEmployeeQuery,
    GetRateQuery,
    GetRatesByEmployeeQuery,
    GetSickLeaveByEmployeeQuery,
    ListBonusesQuery,
    ListRatesQuery,
)
from app.modules.compensation.domain.models import Bonus, Deduction, Overtime, Rate, SickLeave
from app.modules.compensation.domain.repository import (
    BonusRepository,
    DeductionRepository,
    OvertimeRepository,
    RateRepository,
    SickLeaveRepository,
)
from app.modules.compensation.domain.services import (
    CreateBonusService,
    CreateDeductionService,
    CreateOvertimeService,
    CreateRateService,
    CreateSickLeaveService,
)
from app.modules.compensation.infrastructure.read_model import BonusReadModel, RateReadModel


class CreateRateHandler:
    def __init__(self, repository: RateRepository):
        self.repository = repository
        self.service = CreateRateService()

    async def handle(self, command: CreateRateCommand) -> Rate:
        rate = self.service.create(
            employee_id=command.employee_id,
            rate_type=command.rate_type,
            amount=command.amount,
            currency=command.currency,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
            description=command.description,
        )
        return await self.repository.save(rate)


class GetRateHandler:
    def __init__(self, read_model: RateReadModel):
        self.read_model = read_model

    async def handle(self, query: GetRateQuery):
        return await self.read_model.get_by_id(query.rate_id)


class GetRatesByEmployeeHandler:
    def __init__(self, read_model: RateReadModel):
        self.read_model = read_model

    async def handle(self, query: GetRatesByEmployeeQuery):
        return await self.read_model.get_by_employee(query.employee_id)


class GetActiveRateHandler:
    def __init__(self, read_model: RateReadModel):
        self.read_model = read_model

    async def handle(self, query: GetActiveRateQuery):
        return await self.read_model.get_active_rate(query.employee_id, query.check_date)


class ListRatesHandler:
    def __init__(self, read_model: RateReadModel):
        self.read_model = read_model

    async def handle(self, query: ListRatesQuery):
        items, total_count = await self.read_model.list(page=query.page, limit=query.limit)
        return items, total_count


class CreateBonusHandler:
    def __init__(self, repository: BonusRepository):
        self.repository = repository
        self.service = CreateBonusService()

    async def handle(self, command: CreateBonusCommand) -> Bonus:
        bonus = self.service.create(
            employee_id=command.employee_id,
            bonus_type=command.bonus_type,
            amount=command.amount,
            currency=command.currency,
            payment_date=command.payment_date,
            description=command.description,
        )
        return await self.repository.save(bonus)


class GetBonusHandler:
    def __init__(self, read_model: BonusReadModel):
        self.read_model = read_model

    async def handle(self, query: GetBonusQuery):
        return await self.read_model.get_by_id(query.bonus_id)


class GetBonusesByEmployeeHandler:
    def __init__(self, read_model: BonusReadModel):
        self.read_model = read_model

    async def handle(self, query: GetBonusesByEmployeeQuery):
        return await self.read_model.get_by_employee(query.employee_id)


class ListBonusesHandler:
    def __init__(self, read_model: BonusReadModel):
        self.read_model = read_model

    async def handle(self, query: ListBonusesQuery):
        items, total_count = await self.read_model.list(page=query.page, limit=query.limit)
        return items, total_count


class CreateDeductionHandler:
    def __init__(self, repository: DeductionRepository):
        self.repository = repository
        self.service = CreateDeductionService()

    async def handle(self, command: CreateDeductionCommand) -> Deduction:
        deduction = self.service.create(
            employee_id=command.employee_id,
            deduction_type=command.deduction_type,
            amount=command.amount,
            currency=command.currency,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
            description=command.description,
        )
        return await self.repository.save(deduction)


class GetDeductionsByEmployeeHandler:
    def __init__(self, repository: DeductionRepository):
        self.repository = repository

    async def handle(self, query: GetDeductionsByEmployeeQuery) -> List[Deduction]:
        return await self.repository.get_by_employee_id(query.employee_id)


class GetActiveDeductionsHandler:
    def __init__(self, repository: DeductionRepository):
        self.repository = repository

    async def handle(self, query: GetActiveDeductionsQuery) -> List[Deduction]:
        return await self.repository.get_active_deductions(query.employee_id, query.check_date)


class CreateOvertimeHandler:
    def __init__(self, repository: OvertimeRepository):
        self.repository = repository
        self.service = CreateOvertimeService()

    async def handle(self, command: CreateOvertimeCommand) -> Overtime:
        overtime = self.service.create(
            employee_id=command.employee_id,
            multiplier=command.multiplier,
            threshold_hours=command.threshold_hours,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        )
        return await self.repository.save(overtime)


class GetOvertimeByEmployeeHandler:
    def __init__(self, repository: OvertimeRepository):
        self.repository = repository

    async def handle(self, query: GetOvertimeByEmployeeQuery) -> List[Overtime]:
        return await self.repository.get_by_employee_id(query.employee_id)


class CreateSickLeaveHandler:
    def __init__(self, repository: SickLeaveRepository):
        self.repository = repository
        self.service = CreateSickLeaveService()

    async def handle(self, command: CreateSickLeaveCommand) -> SickLeave:
        sick_leave = self.service.create(
            employee_id=command.employee_id,
            percentage=command.percentage,
            max_days=command.max_days,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        )
        return await self.repository.save(sick_leave)


class GetSickLeaveByEmployeeHandler:
    def __init__(self, repository: SickLeaveRepository):
        self.repository = repository

    async def handle(self, query: GetSickLeaveByEmployeeQuery) -> List[SickLeave]:
        return await self.repository.get_by_employee_id(query.employee_id)
