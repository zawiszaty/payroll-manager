from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.absence.domain.entities import Absence, AbsenceBalance
from app.modules.absence.domain.repository import (
    AbsenceBalanceRepository,
    AbsenceRepository,
)
from app.modules.absence.domain.value_objects import AbsenceStatus, AbsenceType
from app.modules.absence.infrastructure.models import (
    AbsenceBalanceModel,
    AbsenceModel,
)
from app.shared.domain.value_objects import DateRange


class SQLAlchemyAbsenceRepository(AbsenceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: AbsenceModel) -> Absence:
        return Absence(
            id=model.id,
            employee_id=model.employee_id,
            absence_type=model.absence_type,
            period=DateRange(model.start_date, model.end_date),
            status=model.status,
            reason=model.reason,
            notes=model.notes,
        )

    def _to_model(self, absence: Absence) -> AbsenceModel:
        return AbsenceModel(
            id=absence.id,
            employee_id=absence.employee_id,
            absence_type=absence.absence_type,
            start_date=absence.period.start_date,
            end_date=absence.period.end_date,
            status=absence.status,
            reason=absence.reason,
            notes=absence.notes,
        )

    async def save(self, absence: Absence) -> Absence:
        model = self._to_model(absence)
        merged = await self.session.merge(model)
        await self.session.flush()
        return self._to_domain(merged)

    async def get_by_id(self, absence_id: UUID) -> Optional[Absence]:
        result = await self.session.execute(
            select(AbsenceModel).where(AbsenceModel.id == absence_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[Absence], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(AbsenceModel)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        result = await self.session.execute(
            select(AbsenceModel).offset(skip).limit(limit).order_by(AbsenceModel.created_at.desc())
        )
        models = result.scalars().all()
        items = [self._to_domain(model) for model in models]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> List[Absence]:
        result = await self.session.execute(
            select(AbsenceModel).where(AbsenceModel.employee_id == employee_id)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_employee_and_status(
        self, employee_id: UUID, status: AbsenceStatus
    ) -> List[Absence]:
        result = await self.session.execute(
            select(AbsenceModel).where(
                and_(
                    AbsenceModel.employee_id == employee_id,
                    AbsenceModel.status == status,
                )
            )
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_approved_for_period(
        self, employee_id: UUID, start_date: date, end_date: date
    ) -> List[Absence]:
        result = await self.session.execute(
            select(AbsenceModel).where(
                and_(
                    AbsenceModel.employee_id == employee_id,
                    AbsenceModel.status == AbsenceStatus.APPROVED,
                    AbsenceModel.start_date <= end_date,
                    AbsenceModel.end_date >= start_date,
                )
            )
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]


class SQLAlchemyAbsenceBalanceRepository(AbsenceBalanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: AbsenceBalanceModel) -> AbsenceBalance:
        return AbsenceBalance(
            id=model.id,
            employee_id=model.employee_id,
            absence_type=model.absence_type,
            year=model.year,
            total_days=model.total_days,
            used_days=model.used_days,
        )

    def _to_model(self, balance: AbsenceBalance) -> AbsenceBalanceModel:
        return AbsenceBalanceModel(
            id=balance.id,
            employee_id=balance.employee_id,
            absence_type=balance.absence_type,
            year=balance.year,
            total_days=balance.total_days,
            used_days=balance.used_days,
        )

    async def save(self, balance: AbsenceBalance) -> AbsenceBalance:
        model = self._to_model(balance)
        merged = await self.session.merge(model)
        await self.session.flush()
        return self._to_domain(merged)

    async def get_by_id(self, balance_id: UUID) -> Optional[AbsenceBalance]:
        result = await self.session.execute(
            select(AbsenceBalanceModel).where(AbsenceBalanceModel.id == balance_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> Tuple[List[AbsenceBalance], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(AbsenceBalanceModel)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        result = await self.session.execute(
            select(AbsenceBalanceModel)
            .offset(skip)
            .limit(limit)
            .order_by(AbsenceBalanceModel.created_at.desc())
        )
        models = result.scalars().all()
        items = [self._to_domain(model) for model in models]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> List[AbsenceBalance]:
        result = await self.session.execute(
            select(AbsenceBalanceModel).where(AbsenceBalanceModel.employee_id == employee_id)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_employee_and_year(self, employee_id: UUID, year: int) -> List[AbsenceBalance]:
        result = await self.session.execute(
            select(AbsenceBalanceModel).where(
                and_(
                    AbsenceBalanceModel.employee_id == employee_id,
                    AbsenceBalanceModel.year == year,
                )
            )
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_employee_type_year(
        self, employee_id: UUID, absence_type: AbsenceType, year: int
    ) -> Optional[AbsenceBalance]:
        result = await self.session.execute(
            select(AbsenceBalanceModel).where(
                and_(
                    AbsenceBalanceModel.employee_id == employee_id,
                    AbsenceBalanceModel.absence_type == absence_type,
                    AbsenceBalanceModel.year == year,
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
