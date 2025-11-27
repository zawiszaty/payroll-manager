from typing import List, Optional
from app.modules.compensation.domain.models import Rate, Bonus, Deduction, Overtime, SickLeave
from app.modules.compensation.domain.repository import (
    RateRepository,
    BonusRepository,
    DeductionRepository,
    OvertimeRepository,
    SickLeaveRepository,
)
from app.modules.compensation.domain.services import (
    CreateRateService,
    CreateBonusService,
    CreateDeductionService,
    CreateOvertimeService,
    CreateSickLeaveService,
)
from app.modules.compensation.application.commands import (
    CreateRateCommand,
    CreateBonusCommand,
    CreateDeductionCommand,
    CreateOvertimeCommand,
    CreateSickLeaveCommand,
)
from app.modules.compensation.application.queries import (
    GetRateQuery,
    GetRatesByEmployeeQuery,
    GetActiveRateQuery,
    ListRatesQuery,
    GetBonusQuery,
    GetBonusesByEmployeeQuery,
    ListBonusesQuery,
    GetDeductionQuery,
    GetDeductionsByEmployeeQuery,
    GetActiveDeductionsQuery,
    GetOvertimeByEmployeeQuery,
    GetSickLeaveByEmployeeQuery,
)


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
        return await self.repository.add(rate)


class GetRateHandler:
    def __init__(self, repository: RateRepository):
        self.repository = repository

    async def handle(self, query: GetRateQuery) -> Optional[Rate]:
        return await self.repository.get_by_id(query.rate_id)


class GetRatesByEmployeeHandler:
    def __init__(self, repository: RateRepository):
        self.repository = repository

    async def handle(self, query: GetRatesByEmployeeQuery) -> List[Rate]:
        return await self.repository.get_by_employee_id(query.employee_id)


class GetActiveRateHandler:
    def __init__(self, repository: RateRepository):
        self.repository = repository

    async def handle(self, query: GetActiveRateQuery) -> Optional[Rate]:
        return await self.repository.get_active_rate(query.employee_id, query.check_date)


class ListRatesHandler:
    def __init__(self, repository: RateRepository):
        self.repository = repository

    async def handle(self, query: ListRatesQuery) -> List[Rate]:
        return await self.repository.list(skip=query.skip, limit=query.limit)


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
        return await self.repository.add(bonus)


class GetBonusHandler:
    def __init__(self, repository: BonusRepository):
        self.repository = repository

    async def handle(self, query: GetBonusQuery) -> Optional[Bonus]:
        return await self.repository.get_by_id(query.bonus_id)


class GetBonusesByEmployeeHandler:
    def __init__(self, repository: BonusRepository):
        self.repository = repository

    async def handle(self, query: GetBonusesByEmployeeQuery) -> List[Bonus]:
        return await self.repository.get_by_employee_id(query.employee_id)


class ListBonusesHandler:
    def __init__(self, repository: BonusRepository):
        self.repository = repository

    async def handle(self, query: ListBonusesQuery) -> List[Bonus]:
        return await self.repository.list(skip=query.skip, limit=query.limit)


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
        return await self.repository.add(deduction)


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
        return await self.repository.add(overtime)


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
        return await self.repository.add(sick_leave)


class GetSickLeaveByEmployeeHandler:
    def __init__(self, repository: SickLeaveRepository):
        self.repository = repository

    async def handle(self, query: GetSickLeaveByEmployeeQuery) -> List[SickLeave]:
        return await self.repository.get_by_employee_id(query.employee_id)
