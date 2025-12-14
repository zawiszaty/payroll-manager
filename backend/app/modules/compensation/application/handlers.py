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
from app.modules.compensation.domain.events import (
    BonusCreatedEvent,
    DeductionCreatedEvent,
    OvertimeCreatedEvent,
    RateCreatedEvent,
    SickLeaveCreatedEvent,
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
from app.shared.domain.events import get_event_dispatcher


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
        saved_rate = await self.repository.save(rate)

        event = RateCreatedEvent(
            rate_id=saved_rate.id,
            employee_id=saved_rate.employee_id,
            rate_type=saved_rate.rate_type.value,
            amount=saved_rate.amount.amount if saved_rate.amount else 0,
            currency=saved_rate.amount.currency if saved_rate.amount else "USD",
            valid_from=saved_rate.date_range.valid_from
            if saved_rate.date_range
            else command.valid_from,
            valid_to=saved_rate.date_range.valid_to if saved_rate.date_range else command.valid_to,
        )
        await get_event_dispatcher().dispatch(event)

        return saved_rate


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
        saved_bonus = await self.repository.save(bonus)

        event = BonusCreatedEvent(
            bonus_id=saved_bonus.id,
            employee_id=saved_bonus.employee_id,
            bonus_type=saved_bonus.bonus_type.value,
            amount=saved_bonus.amount.amount if saved_bonus.amount else 0,
            currency=saved_bonus.amount.currency if saved_bonus.amount else "USD",
            payment_date=saved_bonus.payment_date,
        )
        await get_event_dispatcher().dispatch(event)

        return saved_bonus


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
        saved_deduction = await self.repository.save(deduction)

        event = DeductionCreatedEvent(
            deduction_id=saved_deduction.id,
            employee_id=saved_deduction.employee_id,
            deduction_type=saved_deduction.deduction_type.value,
            amount=saved_deduction.amount.amount if saved_deduction.amount else 0,
            currency=saved_deduction.amount.currency if saved_deduction.amount else "USD",
            valid_from=saved_deduction.date_range.valid_from
            if saved_deduction.date_range
            else command.valid_from,
            valid_to=saved_deduction.date_range.valid_to
            if saved_deduction.date_range
            else command.valid_to,
        )
        await get_event_dispatcher().dispatch(event)

        return saved_deduction


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
        saved_overtime = await self.repository.save(overtime)

        event = OvertimeCreatedEvent(
            overtime_id=saved_overtime.id,
            employee_id=saved_overtime.employee_id,
            multiplier=saved_overtime.rule.multiplier
            if saved_overtime.rule
            else command.multiplier,
            threshold_hours=saved_overtime.rule.threshold_hours
            if saved_overtime.rule
            else command.threshold_hours,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        )
        await get_event_dispatcher().dispatch(event)

        return saved_overtime


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
        saved_sick_leave = await self.repository.save(sick_leave)

        event = SickLeaveCreatedEvent(
            sick_leave_id=saved_sick_leave.id,
            employee_id=saved_sick_leave.employee_id,
            percentage=saved_sick_leave.rule.percentage
            if saved_sick_leave.rule
            else command.percentage,
            max_days=saved_sick_leave.rule.max_days if saved_sick_leave.rule else command.max_days,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        )
        await get_event_dispatcher().dispatch(event)

        return saved_sick_leave


class GetSickLeaveByEmployeeHandler:
    def __init__(self, repository: SickLeaveRepository):
        self.repository = repository

    async def handle(self, query: GetSickLeaveByEmployeeQuery) -> List[SickLeave]:
        return await self.repository.get_by_employee_id(query.employee_id)
