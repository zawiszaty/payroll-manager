from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.application.commands import (
    ApproveAbsenceCommand,
    CancelAbsenceCommand,
    CreateAbsenceBalanceCommand,
    CreateAbsenceCommand,
    RejectAbsenceCommand,
    UpdateAbsenceBalanceCommand,
)
from app.modules.absence.application.queries import (
    GetAbsenceBalanceQuery,
    GetAbsenceBalancesByEmployeeAndYearQuery,
    GetAbsenceBalancesByEmployeeQuery,
    GetAbsenceQuery,
    GetAbsencesByEmployeeAndStatusQuery,
    GetAbsencesByEmployeeQuery,
    ListAbsenceBalancesQuery,
    ListAbsencesQuery,
)
from app.modules.absence.domain.entities import Absence, AbsenceBalance
from app.modules.absence.domain.repository import (
    AbsenceBalanceRepository,
    AbsenceRepository,
)
from app.modules.absence.infrastructure.read_model import (
    AbsenceBalanceReadModel,
    AbsenceReadModel,
)
from app.modules.absence.presentation.schemas import AbsenceBalanceResponse, AbsenceResponse
from app.shared.domain.value_objects import DateRange


class CreateAbsenceHandler:
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        balance_repository: AbsenceBalanceRepository,
    ):
        self.absence_repository = absence_repository
        self.balance_repository = balance_repository

    async def handle(self, command: CreateAbsenceCommand) -> Absence:
        absence = Absence(
            employee_id=command.employee_id,
            absence_type=command.absence_type,
            period=DateRange(command.start_date, command.end_date),
            reason=command.reason,
            notes=command.notes,
        )

        overlapping_absences = await self.absence_repository.get_approved_for_period(
            command.employee_id, command.start_date, command.end_date
        )

        if overlapping_absences:
            raise ValueError("Employee already has approved absence for this period")

        balance = await self.balance_repository.get_by_employee_type_year(
            command.employee_id, command.absence_type, command.start_date.year
        )

        if balance:
            days_needed = absence.calculate_days()
            if not balance.can_take_absence(days_needed):
                raise ValueError(
                    f"Insufficient balance. Requested: {days_needed}, Available: {balance.remaining_days()}"
                )

        return await self.absence_repository.save(absence)


class ApproveAbsenceHandler:
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        balance_repository: AbsenceBalanceRepository,
    ):
        self.absence_repository = absence_repository
        self.balance_repository = balance_repository

    async def handle(self, command: ApproveAbsenceCommand) -> Absence:
        absence = await self.absence_repository.get_by_id(command.absence_id)
        if not absence:
            raise ValueError(f"Absence {command.absence_id} not found")

        absence.approve()

        balance = await self.balance_repository.get_by_employee_type_year(
            absence.employee_id, absence.absence_type, absence.period.start_date.year
        )

        if balance:
            days = absence.calculate_days()
            balance.use_days(days)
            await self.balance_repository.save(balance)

        return await self.absence_repository.save(absence)


class RejectAbsenceHandler:
    def __init__(self, absence_repository: AbsenceRepository):
        self.absence_repository = absence_repository

    async def handle(self, command: RejectAbsenceCommand) -> Absence:
        absence = await self.absence_repository.get_by_id(command.absence_id)
        if not absence:
            raise ValueError(f"Absence {command.absence_id} not found")

        absence.reject()
        return await self.absence_repository.save(absence)


class CancelAbsenceHandler:
    def __init__(
        self,
        absence_repository: AbsenceRepository,
        balance_repository: AbsenceBalanceRepository,
    ):
        self.absence_repository = absence_repository
        self.balance_repository = balance_repository

    async def handle(self, command: CancelAbsenceCommand) -> Absence:
        absence = await self.absence_repository.get_by_id(command.absence_id)
        if not absence:
            raise ValueError(f"Absence {command.absence_id} not found")

        was_approved = absence.status.value == "approved"
        absence.cancel()

        if was_approved:
            balance = await self.balance_repository.get_by_employee_type_year(
                absence.employee_id,
                absence.absence_type,
                absence.period.start_date.year,
            )

            if balance:
                days = absence.calculate_days()
                balance.return_days(days)
                await self.balance_repository.save(balance)

        return await self.absence_repository.save(absence)


class CreateAbsenceBalanceHandler:
    def __init__(self, balance_repository: AbsenceBalanceRepository):
        self.balance_repository = balance_repository

    async def handle(self, command: CreateAbsenceBalanceCommand) -> AbsenceBalance:
        existing = await self.balance_repository.get_by_employee_type_year(
            command.employee_id, command.absence_type, command.year
        )

        if existing:
            raise ValueError(
                f"Balance already exists for employee {command.employee_id}, "
                f"type {command.absence_type}, year {command.year}"
            )

        balance = AbsenceBalance(
            employee_id=command.employee_id,
            absence_type=command.absence_type,
            year=command.year,
            total_days=command.total_days,
        )

        return await self.balance_repository.save(balance)


class UpdateAbsenceBalanceHandler:
    def __init__(self, balance_repository: AbsenceBalanceRepository):
        self.balance_repository = balance_repository

    async def handle(self, command: UpdateAbsenceBalanceCommand) -> AbsenceBalance:
        balance = await self.balance_repository.get_by_id(command.balance_id)
        if not balance:
            raise ValueError(f"Balance {command.balance_id} not found")

        balance.set_total_days(command.total_days)
        return await self.balance_repository.save(balance)


class GetAbsenceHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAbsenceQuery) -> AbsenceResponse:
        read_model = AbsenceReadModel(self.session)
        absence = await read_model.get_by_id(query.absence_id)
        if not absence:
            raise ValueError(f"Absence {query.absence_id} not found")
        return absence


class ListAbsencesHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: ListAbsencesQuery):
        read_model = AbsenceReadModel(self.session)
        items, total_count = await read_model.list(skip=query.skip, limit=query.limit)
        return items, total_count


class GetAbsencesByEmployeeHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAbsencesByEmployeeQuery) -> List[AbsenceResponse]:
        read_model = AbsenceReadModel(self.session)
        return await read_model.get_by_employee(query.employee_id)


class GetAbsencesByEmployeeAndStatusHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAbsencesByEmployeeAndStatusQuery) -> List[AbsenceResponse]:
        read_model = AbsenceReadModel(self.session)
        return await read_model.get_by_employee_and_status(query.employee_id, query.status)


class GetAbsenceBalanceHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAbsenceBalanceQuery) -> AbsenceBalanceResponse:
        read_model = AbsenceBalanceReadModel(self.session)
        balance = await read_model.get_by_id(query.balance_id)
        if not balance:
            raise ValueError(f"Balance {query.balance_id} not found")
        return balance


class ListAbsenceBalancesHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: ListAbsenceBalancesQuery):
        read_model = AbsenceBalanceReadModel(self.session)
        items, total_count = await read_model.list(skip=query.skip, limit=query.limit)
        return items, total_count


class GetAbsenceBalancesByEmployeeHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAbsenceBalancesByEmployeeQuery) -> List[AbsenceBalanceResponse]:
        read_model = AbsenceBalanceReadModel(self.session)
        return await read_model.get_by_employee(query.employee_id)


class GetAbsenceBalancesByEmployeeAndYearHandler:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(
        self, query: GetAbsenceBalancesByEmployeeAndYearQuery
    ) -> List[AbsenceBalanceResponse]:
        read_model = AbsenceBalanceReadModel(self.session)
        return await read_model.get_by_employee_and_year(query.employee_id, query.year)
