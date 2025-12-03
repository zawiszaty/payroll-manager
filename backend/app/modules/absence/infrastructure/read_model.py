from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.domain.value_objects import AbsenceStatus
from app.modules.absence.infrastructure.models import AbsenceBalanceModel, AbsenceModel
from app.modules.absence.presentation.schemas import (
    AbsenceBalanceResponse,
    AbsenceResponse,
)


class AbsenceReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, absence_id: UUID) -> Optional[AbsenceResponse]:
        stmt = select(AbsenceModel).where(AbsenceModel.id == absence_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return AbsenceResponse(
            id=orm.id,
            employee_id=orm.employee_id,
            absence_type=orm.absence_type,
            start_date=orm.start_date,
            end_date=orm.end_date,
            status=orm.status,
            reason=orm.reason,
            notes=orm.notes,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[AbsenceResponse], int]:
        count_stmt = select(func.count()).select_from(AbsenceModel)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(AbsenceModel).offset(skip).limit(limit).order_by(AbsenceModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AbsenceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                start_date=orm.start_date,
                end_date=orm.end_date,
                status=orm.status,
                reason=orm.reason,
                notes=orm.notes,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> list[AbsenceResponse]:
        stmt = (
            select(AbsenceModel)
            .where(AbsenceModel.employee_id == employee_id)
            .order_by(AbsenceModel.start_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            AbsenceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                start_date=orm.start_date,
                end_date=orm.end_date,
                status=orm.status,
                reason=orm.reason,
                notes=orm.notes,
            )
            for orm in orms
        ]

    async def get_by_employee_and_status(
        self, employee_id: UUID, status: AbsenceStatus
    ) -> list[AbsenceResponse]:
        stmt = (
            select(AbsenceModel)
            .where(AbsenceModel.employee_id == employee_id)
            .where(AbsenceModel.status == status)
            .order_by(AbsenceModel.start_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            AbsenceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                start_date=orm.start_date,
                end_date=orm.end_date,
                status=orm.status,
                reason=orm.reason,
                notes=orm.notes,
            )
            for orm in orms
        ]


class AbsenceBalanceReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, balance_id: UUID) -> Optional[AbsenceBalanceResponse]:
        stmt = select(AbsenceBalanceModel).where(AbsenceBalanceModel.id == balance_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        remaining_days = orm.total_days - orm.used_days

        return AbsenceBalanceResponse(
            id=orm.id,
            employee_id=orm.employee_id,
            absence_type=orm.absence_type,
            year=orm.year,
            total_days=orm.total_days,
            used_days=orm.used_days,
            remaining_days=remaining_days,
        )

    async def list(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[AbsenceBalanceResponse], int]:
        count_stmt = select(func.count()).select_from(AbsenceBalanceModel)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        stmt = (
            select(AbsenceBalanceModel)
            .offset(skip)
            .limit(limit)
            .order_by(AbsenceBalanceModel.year.desc(), AbsenceBalanceModel.employee_id)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            AbsenceBalanceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                year=orm.year,
                total_days=orm.total_days,
                used_days=orm.used_days,
                remaining_days=orm.total_days - orm.used_days,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> list[AbsenceBalanceResponse]:
        stmt = (
            select(AbsenceBalanceModel)
            .where(AbsenceBalanceModel.employee_id == employee_id)
            .order_by(AbsenceBalanceModel.year.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            AbsenceBalanceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                year=orm.year,
                total_days=orm.total_days,
                used_days=orm.used_days,
                remaining_days=orm.total_days - orm.used_days,
            )
            for orm in orms
        ]

    async def get_by_employee_and_year(
        self, employee_id: UUID, year: int
    ) -> list[AbsenceBalanceResponse]:
        stmt = (
            select(AbsenceBalanceModel)
            .where(AbsenceBalanceModel.employee_id == employee_id)
            .where(AbsenceBalanceModel.year == year)
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            AbsenceBalanceResponse(
                id=orm.id,
                employee_id=orm.employee_id,
                absence_type=orm.absence_type,
                year=orm.year,
                total_days=orm.total_days,
                used_days=orm.used_days,
                remaining_days=orm.total_days - orm.used_days,
            )
            for orm in orms
        ]
