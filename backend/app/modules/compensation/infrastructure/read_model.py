from datetime import date
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.compensation.infrastructure.models import BonusORM, RateORM
from app.modules.compensation.presentation.views import BonusView, RateView


class RateReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, rate_id: UUID) -> Optional[RateView]:
        stmt = select(RateORM).where(RateORM.id == rate_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return RateView(
            id=orm.id,
            employee_id=orm.employee_id,
            rate_type=orm.rate_type,
            amount=orm.amount,
            currency=orm.currency,
            valid_from=orm.valid_from,
            valid_to=orm.valid_to,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> Tuple[List[RateView], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(RateORM)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        stmt = select(RateORM).offset(skip).limit(limit).order_by(RateORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            RateView(
                id=orm.id,
                employee_id=orm.employee_id,
                rate_type=orm.rate_type,
                amount=orm.amount,
                currency=orm.currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=orm.updated_at.date() if orm.updated_at else None,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> List[RateView]:
        stmt = (
            select(RateORM)
            .where(RateORM.employee_id == employee_id)
            .order_by(RateORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            RateView(
                id=orm.id,
                employee_id=orm.employee_id,
                rate_type=orm.rate_type,
                amount=orm.amount,
                currency=orm.currency,
                valid_from=orm.valid_from,
                valid_to=orm.valid_to,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=orm.updated_at.date() if orm.updated_at else None,
            )
            for orm in orms
        ]

    async def get_active_rate(self, employee_id: UUID, check_date: date) -> Optional[RateView]:
        stmt = (
            select(RateORM)
            .where(RateORM.employee_id == employee_id)
            .where(RateORM.valid_from <= check_date)
            .where((RateORM.valid_to.is_(None)) | (RateORM.valid_to >= check_date))
            .order_by(RateORM.valid_from.desc())
        )
        result = await self.session.execute(stmt)
        orm = result.scalars().first()

        if not orm:
            return None

        return RateView(
            id=orm.id,
            employee_id=orm.employee_id,
            rate_type=orm.rate_type,
            amount=orm.amount,
            currency=orm.currency,
            valid_from=orm.valid_from,
            valid_to=orm.valid_to,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=orm.updated_at.date() if orm.updated_at else None,
        )


class BonusReadModel:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, bonus_id: UUID) -> Optional[BonusView]:
        stmt = select(BonusORM).where(BonusORM.id == bonus_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()

        if not orm:
            return None

        return BonusView(
            id=orm.id,
            employee_id=orm.employee_id,
            bonus_type=orm.bonus_type,
            amount=orm.amount,
            currency=orm.currency,
            payment_date=orm.payment_date,
            description=orm.description,
            created_at=orm.created_at.date() if orm.created_at else None,
            updated_at=None,
        )

    async def list(self, skip: int = 0, limit: int = 100) -> Tuple[List[BonusView], int]:
        # Get total count
        count_stmt = select(func.count()).select_from(BonusORM)
        count_result = await self.session.execute(count_stmt)
        total_count = count_result.scalar_one()

        # Get paginated items
        stmt = select(BonusORM).offset(skip).limit(limit).order_by(BonusORM.created_at.desc())
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        items = [
            BonusView(
                id=orm.id,
                employee_id=orm.employee_id,
                bonus_type=orm.bonus_type,
                amount=orm.amount,
                currency=orm.currency,
                payment_date=orm.payment_date,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=None,
            )
            for orm in orms
        ]

        return items, total_count

    async def get_by_employee(self, employee_id: UUID) -> List[BonusView]:
        stmt = (
            select(BonusORM)
            .where(BonusORM.employee_id == employee_id)
            .order_by(BonusORM.payment_date.desc())
        )
        result = await self.session.execute(stmt)
        orms = result.scalars().all()

        return [
            BonusView(
                id=orm.id,
                employee_id=orm.employee_id,
                bonus_type=orm.bonus_type,
                amount=orm.amount,
                currency=orm.currency,
                payment_date=orm.payment_date,
                description=orm.description,
                created_at=orm.created_at.date() if orm.created_at else None,
                updated_at=None,
            )
            for orm in orms
        ]
